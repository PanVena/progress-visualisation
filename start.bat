@echo off
title Progress - Startup
cd /d "%~dp0"
echo Starting main.py...
py main.py

if %errorlevel% equ 0 goto :eof
echo Error!!! Installing requirements.
py -m pip install -r requirements.txt
py main.py