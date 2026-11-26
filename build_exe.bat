@echo off
setlocal
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
for /f "delims=" %%i in ('python -c "import sys; print(sys.prefix)"') do set PYROOT=%%i
python -m PyInstaller --noconfirm --clean --onefile --windowed --name SQLServerQueryTool --additional-hooks-dir pyinstaller_hooks --paths "%PYROOT%\Lib" --paths "%PYROOT%\DLLs" --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=tkinter.filedialog --hidden-import=tkinter.messagebox --hidden-import=tkinter.simpledialog --hidden-import=_tkinter --add-data "%PYROOT%\tcl\tcl8.6;_tcl_data" --add-data "%PYROOT%\tcl\tk8.6;_tk_data" --add-binary "%PYROOT%\DLLs\tcl86t.dll;." --add-binary "%PYROOT%\DLLs\tk86t.dll;." main.py
if errorlevel 1 exit /b 1
echo.
echo EXE created at dist\SQLServerQueryTool.exe
endlocal
