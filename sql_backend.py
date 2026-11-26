from __future__ import annotations

import ctypes
import json
import os
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path

SETTINGS_PATH = Path(os.environ.get("APPDATA", str(Path.home()))) / "SQLServerQueryTool" / "settings.json"

class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _dpapi_transform(data: bytes, decrypt: bool = False) -> bytes:
    crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    input_buffer = ctypes.create_string_buffer(data, len(data))
    input_blob = _DataBlob(len(data), ctypes.cast(input_buffer, ctypes.POINTER(ctypes.c_byte)))
    output_blob = _DataBlob()
    local_description = wintypes.LPWSTR()
    if decrypt:
        transform = crypt32.CryptUnprotectData
        transform.argtypes = [
            ctypes.POINTER(_DataBlob), ctypes.POINTER(wintypes.LPWSTR),
            ctypes.POINTER(_DataBlob), ctypes.c_void_p, ctypes.c_void_p,
            wintypes.DWORD, ctypes.POINTER(_DataBlob),
        ]
        transform.restype = wintypes.BOOL
        success = transform(
            ctypes.byref(input_blob), ctypes.byref(local_description), None,
            None, None, 0, ctypes.byref(output_blob),
        )
    else:
        transform = crypt32.CryptProtectData
        transform.argtypes = [
            ctypes.POINTER(_DataBlob), wintypes.LPCWSTR, ctypes.POINTER(_DataBlob),
            ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(_DataBlob),
        ]
        transform.restype = wintypes.BOOL
        success = transform(
            ctypes.byref(input_blob), "SQLServerQueryTool password", None,
            None, None, 0, ctypes.byref(output_blob),
        )
    if not success:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(output_blob.pbData, output_blob.cbData)
    finally:
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p
        kernel32.LocalFree(ctypes.cast(output_blob.pbData, ctypes.c_void_p))
        if decrypt and local_description:
            kernel32.LocalFree(ctypes.cast(local_description, ctypes.c_void_p))


@dataclass(frozen=True)
class ConnectionSettings:
    driver: str
    server: str
    database: str
    authentication: str
    username: str
    password: str
    trust_certificate: bool
    remember: bool


class SecureSettingsStore:
    """Loads and saves connection preferences with the password protected by Windows DPAPI."""

    def load(self) -> tuple[dict, bool]:
        try:
            saved = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            encrypted = saved.pop("password_dpapi", "")
            saved["password"] = (
                _dpapi_transform(bytes.fromhex(encrypted), decrypt=True).decode("utf-8")
                if encrypted else ""
            )
            return saved, False
        except FileNotFoundError:
            return {}, False
        except Exception:
            return {}, True

    def save(self, settings: ConnectionSettings) -> str | None:
        try:
            if not settings.remember:
                SETTINGS_PATH.unlink(missing_ok=True)
                return None
            encrypted_password = (
                _dpapi_transform(settings.password.encode("utf-8")).hex()
                if settings.password else ""
            )
            saved = {
                "driver": settings.driver,
                "server": settings.server,
                "database": settings.database,
                "auth": settings.authentication,
                "username": settings.username,
                "trust_cert": settings.trust_certificate,
                "remember": True,
                "password_dpapi": encrypted_password,
            }
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            temporary = SETTINGS_PATH.with_suffix(".tmp")
            temporary.write_text(json.dumps(saved, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(SETTINGS_PATH)
            return None
        except Exception as exc:
            return str(exc)


class SQLServerClient:
    """Owns SQL Server connection-string construction and database operations."""

    @staticmethod
    def build_connection_string(settings: ConnectionSettings) -> str:
        if not settings.driver.strip() or not settings.server.strip():
            raise ValueError("กรุณาระบุ Driver และ Server")

        def odbc_value(text: str) -> str:
            return "{" + text.replace("}", "}}") + "}"

        parts = [f"DRIVER={odbc_value(settings.driver.strip())}", f"SERVER={odbc_value(settings.server.strip())}"]
        if settings.database.strip():
            parts.append(f"DATABASE={odbc_value(settings.database.strip())}")
        if settings.authentication == "Windows":
            parts.append("Trusted_Connection=yes")
        else:
            if not settings.username.strip():
                raise ValueError("กรุณาระบุ Username")
            parts.extend((f"UID={odbc_value(settings.username.strip())}", f"PWD={odbc_value(settings.password)}"))
        parts.append(f"TrustServerCertificate={'yes' if settings.trust_certificate else 'no'}")
        return ";".join(parts) + ";"

    def test_connection(self, settings: ConnectionSettings) -> None:
        import pyodbc
        with pyodbc.connect(self.build_connection_string(settings), timeout=8):
            pass

    def list_databases(self, settings: ConnectionSettings) -> list[str]:
        import pyodbc
        with pyodbc.connect(self.build_connection_string(settings), timeout=8) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sys.databases WHERE HAS_DBACCESS(name) = 1 ORDER BY name;")
            return [str(row[0]) for row in cursor.fetchall()]

    def execute_query(self, settings: ConnectionSettings, sql: str) -> tuple[list[tuple[list[str], list[tuple]]], int]:
        import pyodbc
        result_sets: list[tuple[list[str], list[tuple]]] = []
        with pyodbc.connect(self.build_connection_string(settings), timeout=8, autocommit=True) as connection:
            cursor = connection.cursor()
            cursor.execute(sql)
            while True:
                if cursor.description is not None:
                    columns = [str(item[0]) for item in cursor.description]
                    result_sets.append((columns, cursor.fetchall()))
                if not cursor.nextset():
                    break
            affected_rows = cursor.rowcount
        return result_sets, affected_rows


def available_drivers() -> list[str]:
    try:
        import pyodbc
        installed = pyodbc.drivers()
    except Exception:
        installed = []
    preferred = [d for d in installed if "SQL Server" in d]
    return preferred or ["ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server"]


