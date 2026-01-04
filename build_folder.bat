@echo off
REM Build script for creating EXE with Nuitka (standalone mode for PyQt6)

echo Building executable with Nuitka in standalone mode...
echo.

REM Run Nuitka compilation
python -m nuitka ^
    --standalone ^
    --windows-icon-from-ico=icon.ico ^
    --output-dir=dist ^
    --enable-plugin=pyqt6 ^
    --windows-console-mode=disable ^
    main.py

echo.
echo Build completed! Check the dist/main.dist folder for the executable and all dependencies.
pause
