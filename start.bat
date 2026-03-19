@echo off
title Поступ - Запуск
cd /d "%~dp0"

echo Перевірка файлів...
python -c "import os; lines = open('main.py', encoding='utf-8').readlines() if os.path.exists('main.py') else []; (open('main.py', 'w', encoding='utf-8').writelines(lines[1:]) if lines and lines[0].startswith('#!') else None)" 2>nul
echo Запуск програми...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo Виникла помилка під час запуску. Переконайтеся, що Python встановлено
    echo та виконано команду: pip install -r requirements.txt
    pause
)
