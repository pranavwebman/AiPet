@echo off
echo Building AIPet executable using PyInstaller...

python -m pyinstaller --clean aipet.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo AIPet build succeeded!
    echo Output directory: dist\AIPet\
    echo Executable: dist\AIPet\AIPet.exe
) else (
    echo.
    echo AIPet build failed. Please check error logs above.
)

pause
