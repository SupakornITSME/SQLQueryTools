# SQL Server Query Tool

โปรแกรม GUI สำหรับเชื่อมต่อ SQL Server และรัน SQL พร้อมแสดงผลลัพธ์หลายชุดแยกเป็นแท็บ

## สร้างไฟล์ EXE บน Windows

1. ติดตั้ง Python 3.10 ขึ้นไป และ Microsoft ODBC Driver for SQL Server
2. ดับเบิลคลิก `build_exe.bat`
3. ไฟล์จะอยู่ที่ `dist\SQLServerQueryTool.exe`

สคริปต์จะรวมโมดูล Tkinter, Tcl/Tk และ DLL ที่จำเป็นไว้ในไฟล์ EXE ด้วย

เครื่องปลายทางต้องมี Microsoft ODBC Driver for SQL Server ติดตั้งอยู่ด้วย โปรแกรมรองรับ Windows Authentication และ SQL Server Authentication

โปรแกรมจำข้อมูลการเชื่อมต่อไว้ในโปรไฟล์ Windows เมื่อเลือก `จำข้อมูลเข้าสู่ระบบ` โดยเข้ารหัสรหัสผ่านด้วย Windows DPAPI ซึ่งใช้ได้กับบัญชี Windows เดิมที่บันทึกข้อมูลไว้

## โครงสร้างโค้ด

- `main.py` เป็นจุดเริ่มโปรแกรม และ `sql_frontend.py` ดูแล UI
- `sql_backend.py` มีค่าการเชื่อมต่อ การบันทึกการตั้งค่า และ SQL Server client
- `sql_query_tool.py` คงไว้เป็น compatibility launcher สำหรับการเรียกแบบเดิม
- `ConnectionSettings` เก็บค่าการเชื่อมต่อเป็น object เดียว
- `SecureSettingsStore` โหลดและบันทึกค่าการเชื่อมต่อ โดยเข้ารหัสรหัสผ่านด้วย DPAPI
- `SQLServerClient` สร้าง connection string, ทดสอบการเชื่อมต่อ, โหลดรายชื่อฐานข้อมูล และรัน SQL
- `QueryApp` ดูแลหน้าจอและส่งงานให้คลาสที่รับผิดชอบ

## ใช้งาน

- ใส่ Server เช่น `localhost`, `SERVER\INSTANCE` หรือ `tcp:server,1433`
- คลิกเปิด Dropdown ในช่อง Database เพื่อดึงรายชื่อฐานข้อมูลที่บัญชีมีสิทธิ์เข้าใช้งาน แล้วเลือกรายการได้ หรือพิมพ์ชื่อเองก็ได้
- เลือก Authentication แล้วกรอกข้อมูลให้ครบ
- กด `ทดสอบการเชื่อมต่อ` เพื่อตรวจสอบ หรือกด `Run Query (F5)` เพื่อรัน SQL
- กด `ดูข้อมูลพาเลท` เพื่อกรอก Base Code และดูผลจากตาราง WES/WMS แยกเป็นหลายแท็บ
- กด `นำ Shuttle Car ออกจาก Segment` กรอกรหัสรถ แล้วยืนยันก่อนลบข้อมูล Claim
- กด `นำ Shuttle Car เข้า Segment เพื่อทำงาน` แล้วกรอกรหัสรถ เลือก Segment ID จาก Dropdown (ID 19–38) หรือ Target Location จากนั้นเลือก Auto/Manual และยืนยันก่อนเรียก Stored Procedure
- กด `เปลี่ยนโหมด Shuttle Car` เพื่อกรอกรหัสรถ เลือก Status Code (`Active`, `ManualControl`, `Maintenance`) แล้วยืนยันก่อนอัปเดตสถานะ

ใช้บัญชีที่มีสิทธิ์เท่าที่จำเป็น และตรวจสอบ SQL ก่อนรันคำสั่งที่แก้ไขข้อมูล
