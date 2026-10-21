@echo off
setlocal
cd /d "%~dp0"
if not defined JAVASCRIPT_OBFUSCATOR_HOME if exist "D:\_Vasyl\Program Files\javascript-obfuscator\bin\javascript-obfuscator" set "JAVASCRIPT_OBFUSCATOR_HOME=D:\_Vasyl\Program Files\javascript-obfuscator"
if not defined PJORION_HOME set "PJORION_HOME=D:\_Vasyl\Program Files\PjOrion_1.3.5_11.08.2019"
"C:\Python314\python.exe" build_protected_2.0.py %*
set "build_code=%errorlevel%"

echo.
echo ==========================
if "%build_code%"=="0" (
    echo Protected build completed.
) else (
    echo Protected build failed with code %build_code%.
)
echo ==========================
pause
exit /b %build_code%
