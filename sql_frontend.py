from __future__ import annotations

import os
import sys
import threading

if getattr(sys, "frozen", False):
    os.environ.setdefault("TCL_LIBRARY", os.path.join(sys._MEIPASS, "_tcl_data"))
    os.environ.setdefault("TK_LIBRARY", os.path.join(sys._MEIPASS, "_tk_data"))

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from sql_backend import ConnectionSettings, SQLServerClient, SecureSettingsStore, available_drivers

APP_TITLE = "SQL Server Query Tool"
SEGMENTS = (
    (19, "LV01-RACK-LANE-04", "Segment Left 1-19 LV01"),
    (20, "LV01-RACK-LANE-35", "Segment Left 20-38 LV01"),
    (21, "LV02-RACK-LANE-04", "Segment Left 1-19 LV02"),
    (22, "LV02-RACK-LANE-35", "Segment Left 20-38 LV02"),
    (23, "LV03-RACK-LANE-04", "Segment Left 1-19 LV03"),
    (24, "LV03-RACK-LANE-35", "Segment Left 20-38 LV03"),
    (25, "LV04-RACK-LANE-04", "Segment Left 1-19 LV04"),
    (26, "LV04-RACK-LANE-35", "Segment Left 20-38 LV04"),
    (27, "LV05-RACK-LANE-04", "Segment Left 1-19 LV05"),
    (28, "LV05-RACK-LANE-35", "Segment Left 20-38 LV05"),
    (29, "LV06-RACK-LANE-04", "Segment Left 1-19 LV06"),
    (30, "LV06-RACK-LANE-35", "Segment Left 20-38 LV06"),
    (31, "LV07-RACK-LANE-04", "Segment Left 1-19 LV07"),
    (32, "LV07-RACK-LANE-35", "Segment Left 20-38 LV07"),
    (33, "LV08-RACK-LANE-04", "Segment Left 1-19 LV08"),
    (34, "LV08-RACK-LANE-35", "Segment Left 20-38 LV08"),
    (35, "LV09-RACK-LANE-04", "Segment Left 1-19 LV09"),
    (36, "LV09-RACK-LANE-35", "Segment Left 20-38 LV09"),
    (37, "LV10-RACK-LANE-04", "Segment Left 1-19 LV10"),
    (38, "LV10-RACK-LANE-35", "Segment Left 20-38 LV10"),
)

class QueryApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.settings_store = SecureSettingsStore()
        self.sql_client = SQLServerClient()
        self._saved_settings, self._settings_load_error = self.settings_store.load()
        self.title(APP_TITLE)
        self.geometry("1180x820")
        self.minsize(920, 650)
        self._busy = False
        self._db_loaded = False
        self._setup_style()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        if self._settings_load_error:
            self.status.set("โหลดการตั้งค่าที่บันทึกไว้ไม่สำเร็จ กรุณาตรวจสอบข้อมูลการเชื่อมต่อ")

    def _setup_style(self) -> None:
        self.configure(background="#f9f1f6")
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", font=("Segoe UI", 9))
        style.configure("TFrame", background="#a8ccf1")
        style.configure("Card.TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", foreground="#334155")
        style.configure("AppTitle.TLabel", background="#a8ccf1", foreground="#0f172a", font=("Segoe UI", 19, "bold"))
        style.configure("AppSubtitle.TLabel", background="#a8ccf1", foreground="#64748b", font=("Segoe UI", 9))
        style.configure("TLabelframe", background="#ffffff", bordercolor="#dbe3ed", borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", background="#ffffff", foreground="#0f172a", font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", padding=(7, 6), fieldbackground="#ffffff", bordercolor="#cbd5e1")
        style.configure("TCombobox", padding=(7, 5), fieldbackground="#ffffff", bordercolor="#cbd5e1", arrowsize=13)
        style.configure("TButton", padding=(10, 7), background="#e2e8f0", foreground="#1e293b", borderwidth=0, font=("Segoe UI", 9, "bold"))
        style.map("TButton", background=[("active", "#cbd5e1"), ("disabled", "#e2e8f0")])
        style.configure("Primary.TButton", background="#2563eb", foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#1d4ed8"), ("disabled", "#93c5fd")], foreground=[("disabled", "#ffffff")])
        style.configure("Danger.TButton", background="#fee2e2", foreground="#b91c1c")
        style.map("Danger.TButton", background=[("active", "#fecaca")])
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#1e293b", rowheight=27, borderwidth=0, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#eaf0f7", foreground="#334155", padding=(8, 7), font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#1e3a8a")])
        style.configure("TNotebook", background="#ffffff", borderwidth=0, tabmargins=(2, 4, 2, 0))
        style.configure("TNotebook.Tab", background="#eaf0f7", foreground="#475569", padding=(11, 7), font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#2563eb"), ("active", "#dbeafe")], foreground=[("selected", "#ffffff")])
        style.configure("Status.TLabel", background="#e2e8f0", foreground="#334155", padding=(10, 7), font=("Segoe UI", 9))

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=2)
        header = ttk.Frame(self, style="TFrame", padding=(16, 14, 16, 5))
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="SQL Server Query Tool", style="AppTitle.TLabel").pack(anchor="w")
        ttk.Label(header, text="เชื่อมต่อฐานข้อมูล  •  เขียน SQL  •  จัดการ Shuttle และ Pallet", style="AppSubtitle.TLabel").pack(anchor="w", pady=(2, 0))

        conn = ttk.LabelFrame(self, text="การเชื่อมต่อ SQL Server", padding=12)
        conn.grid(row=1, column=0, sticky="ew", padx=16, pady=6)
        for col, weight in ((1, 2), (3, 2), (5, 1)):
            conn.columnconfigure(col, weight=weight)

        saved = self._saved_settings
        drivers = available_drivers()
        self.driver = tk.StringVar(value=saved.get("driver") or drivers[0])
        self.server = tk.StringVar(value=saved.get("server", ""))
        self.database = tk.StringVar(value=saved.get("database", ""))
        self.auth = tk.StringVar(value=saved.get("auth", "Windows"))
        self.username = tk.StringVar(value=saved.get("username", ""))
        self.password = tk.StringVar(value=saved.get("password", ""))
        self.trust_cert = tk.BooleanVar(value=saved.get("trust_cert", True))
        self.remember_settings = tk.BooleanVar(value=saved.get("remember", True))
        for variable in (self.driver, self.server, self.auth, self.username, self.password):
            variable.trace_add("write", self._invalidate_database_list)
        ttk.Label(conn, text="Driver").grid(row=0, column=0, sticky="w", padx=3, pady=3)
        ttk.Combobox(conn, textvariable=self.driver, values=available_drivers(), width=28).grid(row=0, column=1, sticky="ew", padx=3, pady=3)
        ttk.Label(conn, text="Server").grid(row=0, column=2, sticky="w", padx=3, pady=3)
        ttk.Entry(conn, textvariable=self.server).grid(row=0, column=3, columnspan=3, sticky="ew", padx=3, pady=3)
        ttk.Label(conn, text="Database (ไม่บังคับ)").grid(row=1, column=0, sticky="w", padx=3, pady=3)
        self.database_combo = ttk.Combobox(
            conn, textvariable=self.database, width=28, postcommand=self.load_databases
        )
        self.database_combo.grid(row=1, column=1, columnspan=2, sticky="ew", padx=3, pady=3)
        ttk.Label(conn, text="Authentication").grid(row=1, column=3, sticky="w", padx=3, pady=3)
        auth = ttk.Combobox(conn, textvariable=self.auth, values=("Windows", "SQL Server"), state="readonly", width=15)
        auth.grid(row=1, column=4, columnspan=2, sticky="ew", padx=3, pady=3)
        auth.bind("<<ComboboxSelected>>", self._auth_changed)
        ttk.Label(conn, text="Username").grid(row=2, column=0, sticky="w", padx=3, pady=3)
        self.user_entry = ttk.Entry(conn, textvariable=self.username, state="disabled")
        self.user_entry.grid(row=2, column=1, sticky="ew", padx=3, pady=3)
        ttk.Label(conn, text="Password").grid(row=2, column=2, sticky="w", padx=3, pady=3)
        self.pass_entry = ttk.Entry(conn, textvariable=self.password, show="•", state="disabled")
        self.pass_entry.grid(row=2, column=3, sticky="ew", padx=3, pady=3)
        options = ttk.Frame(conn, style="Card.TFrame")
        options.grid(row=2, column=4, sticky="w", padx=3)
        ttk.Checkbutton(options, text="Trust certificate", variable=self.trust_cert).pack(anchor="w")
        ttk.Checkbutton(
            options, text="จำข้อมูลเข้าสู่ระบบ", variable=self.remember_settings,
            command=self._remember_toggled,
        ).pack(anchor="w")
        self.connect_btn = ttk.Button(conn, text="ทดสอบการเชื่อมต่อ", command=self.test_connection)
        self.connect_btn.grid(row=2, column=5, sticky="e", padx=3, pady=3)
        self._auth_changed()

        editor = ttk.LabelFrame(self, text="SQL Query", padding=12)
        editor.grid(row=2, column=0, sticky="nsew", padx=16, pady=6)
        editor.columnconfigure(0, weight=1)
        editor.rowconfigure(0, weight=1)
        self.query = tk.Text(editor, height=10, wrap="none", undo=True, font=("Consolas", 10), bg="#ffffff", fg="#0f172a", insertbackground="#2563eb", selectbackground="#bfdbfe", selectforeground="#0f172a", relief="flat", padx=10, pady=9, highlightthickness=1, highlightbackground="#dbe3ed", highlightcolor="#60a5fa")
        ybar = ttk.Scrollbar(editor, orient="vertical", command=self.query.yview)
        xbar = ttk.Scrollbar(editor, orient="horizontal", command=self.query.xview)
        self.query.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        self.query.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        self.query.insert("1.0", "SELECT TOP (100) name, create_date\nFROM sys.databases\nORDER BY name;")
        actions = ttk.Frame(editor, style="Card.TFrame")
        actions.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(7, 0))
        self.run_btn = ttk.Button(actions, text="Run Query  F5", command=self.run_query, style="Primary.TButton")
        self.run_btn.pack(side="left")
        ttk.Button(actions, text="ดูข้อมูลพาเลท", command=self.view_pallet).pack(side="left", padx=(8, 0))
        ttk.Button(actions, text="นำ Shuttle Car ออกจาก Segment", command=self.remove_shuttle_from_segment, style="Danger.TButton").pack(side="left", padx=6)
        ttk.Button(actions, text="นำ Shuttle Car เข้า Segment เพื่อทำงาน", command=self.add_shuttle_to_segment).pack(side="left", padx=6)
        ttk.Button(actions, text="เปลี่ยนโหมด Shuttle Car", command=self.change_shuttle_mode).pack(side="left", padx=6)
        ttk.Button(actions, text="ล้าง Query", command=lambda: self.query.delete("1.0", "end")).pack(side="left", padx=6)
        self.bind("<F5>", lambda _event: self.run_query())

        results = ttk.LabelFrame(self, text="ผลลัพธ์", padding=12)
        results.grid(row=3, column=0, sticky="nsew", padx=16, pady=(6, 10))
        results.columnconfigure(0, weight=1)
        results.rowconfigure(0, weight=1)
        self.results_notebook = ttk.Notebook(results)
        self.results_notebook.grid(row=0, column=0, sticky="nsew")
        self.status = tk.StringVar(value="พร้อมใช้งาน")
        ttk.Label(self, textvariable=self.status, style="Status.TLabel", anchor="w").grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 10))

    def _auth_changed(self, _event=None) -> None:
        state = "normal" if self.auth.get() == "SQL Server" else "disabled"
        self.user_entry.configure(state=state)
        self.pass_entry.configure(state=state)

    def _invalidate_database_list(self, *_args) -> None:
        self._db_loaded = False

    def _save_connection_settings(self) -> str | None:
        return self.settings_store.save(self._connection_settings())

    def _remember_toggled(self) -> None:
        error = self._save_connection_settings()
        if error:
            messagebox.showwarning("บันทึกการตั้งค่าไม่ได้", error, parent=self)

    def _on_close(self) -> None:
        error = self._save_connection_settings()
        if error:
            messagebox.showwarning("บันทึกการตั้งค่าไม่ได้", error, parent=self)
        self.destroy()

    def _connection_settings(self) -> ConnectionSettings:
        return ConnectionSettings(
            driver=self.driver.get(),
            server=self.server.get(),
            database=self.database.get(),
            authentication=self.auth.get(),
            username=self.username.get(),
            password=self.password.get(),
            trust_certificate=self.trust_cert.get(),
            remember=self.remember_settings.get(),
        )

    def _connection_string(self) -> str:
        return self.sql_client.build_connection_string(self._connection_settings())

    def _start(self, button: ttk.Button | None, status: str) -> bool:
        if self._busy:
            return False
        self._busy = True
        self.run_btn.configure(state="disabled")
        self.connect_btn.configure(state="disabled")
        if button is not None:
            button.configure(state="disabled")
        self.status.set(status)
        return True

    def _finish(self, message: str) -> None:
        self._busy = False
        self.run_btn.configure(state="normal")
        self.connect_btn.configure(state="normal")
        self.status.set(message)

    def load_databases(self) -> None:
        if self._db_loaded:
            return
        try:
            # Use the same connection context as Query; some restricted SQL logins
            # cannot open master explicitly even though their default DB is available.
            settings = self._connection_settings()
            self.sql_client.build_connection_string(settings)
        except ValueError as exc:
            messagebox.showerror("ข้อมูลไม่ครบ", str(exc))
            return
        self._save_connection_settings()
        if not self._start(None, "กำลังโหลดรายชื่อฐานข้อมูล..."):
            return

        def work() -> None:
            try:
                databases = self.sql_client.list_databases(settings)
                self.after(0, lambda values=databases: self._database_list_loaded(values))
                self.after(0, lambda count=len(databases): self._finish(f"โหลดรายชื่อฐานข้อมูลแล้ว {count} รายการ"))
            except Exception as exc:
                self.after(0, lambda error=str(exc): (self._finish("โหลดรายชื่อฐานข้อมูลไม่สำเร็จ"), messagebox.showerror("โหลดรายชื่อฐานข้อมูลไม่สำเร็จ", error)))
        threading.Thread(target=work, daemon=True).start()

    def _database_list_loaded(self, databases: list[str]) -> None:
        self.database_combo.configure(values=databases)
        self._db_loaded = True
        self.after_idle(lambda: self.database_combo.event_generate("<Down>"))

    def test_connection(self) -> None:
        try:
            settings = self._connection_settings()
            self.sql_client.build_connection_string(settings)
        except ValueError as exc:
            messagebox.showerror("ข้อมูลไม่ครบ", str(exc))
            return
        self._save_connection_settings()
        if not self._start(self.connect_btn, "กำลังเชื่อมต่อ..."):
            return

        def work() -> None:
            try:
                self.sql_client.test_connection(settings)
                self.after(0, lambda: (self._finish("เชื่อมต่อสำเร็จ"), messagebox.showinfo("สำเร็จ", "เชื่อมต่อ SQL Server สำเร็จ")))
            except Exception as exc:
                self.after(0, lambda error=str(exc): (self._finish("เชื่อมต่อไม่สำเร็จ"), messagebox.showerror("เชื่อมต่อไม่สำเร็จ", error)))
        threading.Thread(target=work, daemon=True).start()

    def run_query(self) -> None:
        self._execute_query(self.query.get("1.0", "end-1c").strip())

    def view_pallet(self) -> None:
        base = simpledialog.askstring(
            "ดูข้อมูลพาเลท", "กรอก Base Code:", initialvalue="3116045912", parent=self
        )
        if base is None:
            return
        base = base.strip()
        if not base:
            messagebox.showerror("ข้อมูลไม่ครบ", "กรุณากรอก Base Code")
            return
        base_literal = base.replace("'", "''")
        sql = f"""SET NOCOUNT ON;
DECLARE @base NVARCHAR(MAX) = N'{base_literal}';
DECLARE @unit INT;
DECLARE @item INT;
DECLARE @Task INT;

SELECT @unit = storage_unit_id FROM wms.trx_storage_unit WHERE base_code = @base;
SELECT @item = storage_item_id FROM wms.trx_storage_item WHERE storage_unit_id = @unit;
SELECT @Task = task_works_id FROM wes.trx_task_works WHERE base_code = @base;

SELECT * FROM wes.trx_task_works_extend WHERE task_works_id = @Task;
SELECT * FROM wes.trx_task_works WHERE task_works_id = @Task;
SELECT * FROM wes.trx_task_works_status WHERE task_works_id = @Task;
SELECT * FROM wes.trx_task_machine_work WHERE task_works_id = @Task;
SELECT * FROM wes.trx_transit_work WHERE task_works_id = @Task;
SELECT * FROM wes.trx_location WHERE task_works_id = @Task OR base_code = @base;
SELECT * FROM wms.trx_storage_unit WHERE base_code = @base;
SELECT * FROM wms.trx_storage_item WHERE storage_unit_id = @unit;
SELECT * FROM wms.trx_storage_activity
WHERE from_storage_unit_id = @unit OR to_storage_unit_id = @unit
   OR from_storage_item_id = @item OR to_storage_item_id = @item
ORDER BY storage_activity_id DESC;
SELECT * FROM wes.trx_putaway
WHERE storage_item_id IN (SELECT storage_item_id FROM wms.trx_storage_item WHERE storage_unit_id = @unit);
SELECT * FROM wes.set_base WHERE base_code = @base;"""
        self.query.delete("1.0", "end")
        self.query.insert("1.0", sql)
        labels = [
            "wes.trx_task_works_extend", "wes.trx_task_works", "wes.trx_task_works_status",
            "wes.trx_task_machine_work", "wes.trx_transit_work", "wes.trx_location",
            "wms.trx_storage_unit", "wms.trx_storage_item", "wms.trx_storage_activity",
            "wes.trx_putaway", "wes.set_base",
        ]
        self._execute_query(sql, labels)

    def remove_shuttle_from_segment(self) -> None:
        shuttle_code = simpledialog.askstring(
            "นำ Shuttle Car ออกจาก Segment",
            "กรอกรหัส Shuttle Car:",
            initialvalue="Shu01",
            parent=self,
        )
        if shuttle_code is None:
            return
        shuttle_code = shuttle_code.strip()
        if not shuttle_code:
            messagebox.showerror("ข้อมูลไม่ครบ", "กรุณากรอกรหัส Shuttle Car")
            return
        if not messagebox.askyesno(
            "ยืนยันการลบ",
            f"ยืนยันนำ Shuttle Car '{shuttle_code}' ออกจาก Segment?\nข้อมูล Claim ของรถคันนี้จะถูกลบ",
            parent=self,
        ):
            return

        shuttle_literal = shuttle_code.replace("'", "''")
        sql = f"""SET NOCOUNT ON;
DECLARE @Shu NVARCHAR(MAX) = N'{shuttle_literal}';
DECLARE @mcID INT;
SELECT @mcID = mc_id
FROM wcs.set_machine
WHERE mc_code IN (SELECT mc_code FROM wcs.set_machine WHERE mc_code = @Shu);
IF @mcID IS NULL
    THROW 50001, 'Shuttle Car code was not found in wcs.set_machine.', 1;
DELETE FROM shuttle.set_shuttle_segment_claim WHERE mc_id = @mcID;
SELECT @Shu AS mc_code, @mcID AS mc_id, @@ROWCOUNT AS deleted_claim_rows;"""
        self.query.delete("1.0", "end")
        self.query.insert("1.0", sql)
        self._execute_query(sql, ["ผลการนำ Shuttle Car ออกจาก Segment"])

    def add_shuttle_to_segment(self) -> None:
        shuttle_code = simpledialog.askstring(
            "นำ Shuttle Car เข้า Segment เพื่อทำงาน",
            "กรอกรหัส Shuttle Car (@mc_code):",
            parent=self,
        )
        if shuttle_code is None:
            return
        shuttle_code = shuttle_code.strip()
        if not shuttle_code or len(shuttle_code) > 20:
            messagebox.showerror("ข้อมูลไม่ถูกต้อง", "กรุณากรอกรหัส Shuttle Car ความยาวไม่เกิน 20 ตัวอักษร")
            return

        segment_choice = self._choose_segment_id()
        if segment_choice is None:
            return
        target_segment_id = None
        target_location = None
        if segment_choice == "target_location":
            target_location = simpledialog.askstring(
                "ระบุ Target Location",
                "กรอก Location ภายใน Segment:",
                parent=self,
            )
            if target_location is None:
                return
            target_location = target_location.strip()
            if not target_location or len(target_location) > 20:
                messagebox.showerror("ข้อมูลไม่ถูกต้อง", "กรุณากรอก Target Location ความยาวไม่เกิน 20 ตัวอักษร")
                return
        else:
            target_segment_id = int(segment_choice)

        job_auto = messagebox.askyesno(
            "รูปแบบ Job",
            "สร้าง Job อัตโนมัติหรือไม่?\nเลือก No หากต้องการสร้าง Job แบบ Manual",
            parent=self,
            default="yes",
        )
        if target_segment_id is not None:
            target_description = f"Segment ID {target_segment_id}"
        else:
            target_description = f"Location {target_location}"
        if not messagebox.askyesno(
            "ยืนยันการสร้าง Segment Claim Job",
            f"ยืนยันนำ Shuttle Car '{shuttle_code}' เข้า {target_description}?\n"
            f"โหมด Job: {'Auto' if job_auto else 'Manual'}",
            parent=self,
        ):
            return

        code_sql = shuttle_code.replace("'", "''")
        location_sql = "NULL" if target_location is None else "'" + target_location.replace("'", "''") + "'"
        segment_sql = "NULL" if target_segment_id is None else str(target_segment_id)
        sql = f"""SET NOCOUNT ON;
DECLARE @RC INT;
DECLARE @mc_code VARCHAR(20) = '{code_sql}';
DECLARE @target_segment_id INT = {segment_sql};
DECLARE @target_location VARCHAR(20) = {location_sql};
DECLARE @job_auto BIT = {1 if job_auto else 0};
DECLARE @result_id SMALLINT;
DECLARE @result_msg NVARCHAR(500);

EXECUTE @RC = [shuttle].[sp_shuttle_create_segment_claim_job]
    @mc_code,
    @target_segment_id,
    @target_location,
    @job_auto,
    @result_id OUTPUT,
    @result_msg OUTPUT;

SELECT @result_id AS result_id, @result_msg AS result_msg;
SELECT * FROM wes.trx_machine_job;
SELECT * FROM [shuttle].[set_shuttle]
WHERE mc_id IN (SELECT mc_id FROM wcs.set_machine WHERE mc_code = @mc_code);
SELECT * FROM [shuttle].[set_shuttle_segment_claim]
WHERE mc_id IN (SELECT mc_id FROM wcs.set_machine WHERE mc_code = @mc_code);"""
        self.query.delete("1.0", "end")
        self.query.insert("1.0", sql)
        self._execute_query(
            sql,
            [
                "ผลการสร้าง Segment Claim Job",
                "wes.trx_machine_job",
                "shuttle.set_shuttle",
                "shuttle.set_shuttle_segment_claim",
            ],
        )

    def _choose_segment_id(self) -> int | str | None:
        segment_labels = [
            f"{segment_id} | {code} | {description}"
            for segment_id, code, description in SEGMENTS
        ]
        location_option = "ระบุ Target Location แทน"
        options = segment_labels + [location_option]
        dialog = tk.Toplevel(self)
        dialog.title("เลือก Segment ID")
        dialog.transient(self)
        dialog.resizable(False, False)
        dialog.grab_set()
        ttk.Label(dialog, text="เลือก Segment ID:").grid(
            row=0, column=0, sticky="w", padx=12, pady=(12, 6)
        )
        selected = tk.StringVar(value=segment_labels[0])
        combo = ttk.Combobox(
            dialog, textvariable=selected, values=options, state="readonly", width=54
        )
        combo.grid(row=1, column=0, sticky="ew", padx=12, pady=4)
        result: dict[str, int | str | None] = {"value": None}

        def accept() -> None:
            choice = selected.get()
            if choice == location_option:
                result["value"] = "target_location"
            else:
                result["value"] = int(choice.split("|", 1)[0].strip())
            dialog.destroy()

        def cancel() -> None:
            dialog.destroy()

        buttons = ttk.Frame(dialog)
        buttons.grid(row=2, column=0, sticky="e", padx=12, pady=(8, 12))
        ttk.Button(buttons, text="ตกลง", command=accept).pack(side="left", padx=(0, 6))
        ttk.Button(buttons, text="ยกเลิก", command=cancel).pack(side="left")
        dialog.bind("<Return>", lambda _event: accept())
        dialog.protocol("WM_DELETE_WINDOW", cancel)
        combo.current(0)
        combo.focus_set()
        dialog.update_idletasks()
        width, height = dialog.winfo_reqwidth(), dialog.winfo_reqheight()
        x = (dialog.winfo_screenwidth() - width) // 2
        y = (dialog.winfo_screenheight() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        self.wait_window(dialog)
        return result["value"]

    def change_shuttle_mode(self) -> None:
        shuttle_code = simpledialog.askstring(
            "เปลี่ยนโหมด Shuttle Car",
            "กรอกรหัส Shuttle Car (@Shu):",
            initialvalue="Shu08",
            parent=self,
        )
        if shuttle_code is None:
            return
        shuttle_code = shuttle_code.strip()
        if not shuttle_code:
            messagebox.showerror("ข้อมูลไม่ครบ", "กรุณากรอกรหัส Shuttle Car")
            return

        status_code = self._choose_shuttle_status()
        if status_code is None:
            return
        if not messagebox.askyesno(
            "ยืนยันการเปลี่ยนโหมด",
            f"ยืนยันเปลี่ยนโหมด Shuttle Car '{shuttle_code}' เป็น '{status_code}'?",
            parent=self,
        ):
            return

        shuttle_literal = shuttle_code.replace("'", "''")
        status_literal = status_code.replace("'", "''")
        sql = f"""SET NOCOUNT ON;
DECLARE @Shu NVARCHAR(MAX) = N'{shuttle_literal}';
DECLARE @StatusCar NVARCHAR(MAX) = N'{status_literal}';
DECLARE @mcID INT;
SELECT @mcID = mc_id
FROM wcs.set_machine
WHERE mc_code IN (SELECT mc_code FROM wcs.set_machine WHERE mc_code = @Shu);
IF @mcID IS NULL
    THROW 50002, 'Shuttle Car code was not found in wcs.set_machine.', 1;
UPDATE shuttle.set_shuttle
SET status_code = @StatusCar
WHERE mc_id = @mcID;
SELECT @Shu AS mc_code, @StatusCar AS status_code, @@ROWCOUNT AS updated_rows;"""
        self.query.delete("1.0", "end")
        self.query.insert("1.0", sql)
        self._execute_query(sql, ["ผลการเปลี่ยนโหมด Shuttle Car"])

    def _choose_shuttle_status(self) -> str | None:
        dialog = tk.Toplevel(self)
        dialog.title("เลือก Status Code")
        dialog.transient(self)
        dialog.resizable(False, False)
        dialog.grab_set()

        status = tk.StringVar(value="Active")
        ttk.Label(dialog, text="เลือก Status Code:").grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 6)
        )
        combo = ttk.Combobox(
            dialog,
            textvariable=status,
            values=("Active", "ManualControl", "Maintenance"),
            state="readonly",
            width=28,
        )
        combo.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=4)
        result: dict[str, str | None] = {"value": None}

        def accept() -> None:
            result["value"] = status.get()
            dialog.destroy()

        def cancel() -> None:
            dialog.destroy()

        ttk.Button(dialog, text="ตกลง", command=accept).grid(
            row=2, column=0, sticky="ew", padx=(12, 4), pady=(8, 12)
        )
        ttk.Button(dialog, text="ยกเลิก", command=cancel).grid(
            row=2, column=1, sticky="ew", padx=(4, 12), pady=(8, 12)
        )
        dialog.bind("<Return>", lambda _event: accept())
        dialog.protocol("WM_DELETE_WINDOW", cancel)
        combo.current(0)
        combo.focus_set()
        dialog.update_idletasks()
        width, height = dialog.winfo_reqwidth(), dialog.winfo_reqheight()
        x = (dialog.winfo_screenwidth() - width) // 2
        y = (dialog.winfo_screenheight() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        self.wait_window(dialog)
        return result["value"]

    def _execute_query(self, sql: str, result_labels: list[str] | None = None) -> None:
        if not sql:
            return
        try:
            settings = self._connection_settings()
            self.sql_client.build_connection_string(settings)
        except ValueError as exc:
            messagebox.showerror("ข้อมูลไม่ครบ", str(exc))
            return
        self._save_connection_settings()
        if not self._start(self.run_btn, "กำลังรัน Query..."):
            return
        for tab_id in self.results_notebook.tabs():
            self.results_notebook.forget(tab_id)

        def work() -> None:
            try:
                result_sets, affected_rows = self.sql_client.execute_query(settings, sql)
                if result_sets:
                    self.after(0, lambda rs=result_sets, names=result_labels: self._show_results(rs, names))
                    row_count = sum(len(rows) for _, rows in result_sets)
                    summary = f"สำเร็จ: {len(result_sets)} ชุดผลลัพธ์, {row_count:,} แถว"
                else:
                    summary = f"สำเร็จ: คำสั่งทำงานแล้ว ({affected_rows} แถวได้รับผลกระทบ)"
                self.after(0, lambda msg=summary: self._finish(msg))
            except Exception as exc:
                self.after(0, lambda error=str(exc): (self._finish("Query มีข้อผิดพลาด"), messagebox.showerror("Query มีข้อผิดพลาด", error)))
        threading.Thread(target=work, daemon=True).start()

    def _show_results(self, result_sets: list[tuple[list[str], list[tuple]]], labels: list[str] | None = None) -> None:
        for index, (columns, rows) in enumerate(result_sets):
            frame = ttk.Frame(self.results_notebook)
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(1, weight=1)
            label = labels[index] if labels and index < len(labels) else f"ผลลัพธ์ {index + 1}"
            ttk.Label(frame, text=label, anchor="w").grid(
                row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 6)
            )
            tree = ttk.Treeview(frame, show="headings", columns=columns)
            tree_y = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree_x = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=tree_y.set, xscrollcommand=tree_x.set)
            tree.grid(row=1, column=0, sticky="nsew")
            tree_y.grid(row=1, column=1, sticky="ns")
            tree_x.grid(row=2, column=0, sticky="ew")
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, minwidth=70, stretch=True)
            for row in rows:
                tree.insert("", "end", values=["NULL" if value is None else str(value) for value in row])
            self.results_notebook.add(frame, text=f"{index + 1}. {label}")

