#!/usr/bin/env python3
"""Читає data.json і оновлює EMBEDDED_DATA та дату в index.html."""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

DIR = Path(__file__).parent.parent
DATA_JSON = DIR / "data.json"
INDEX_HTML = DIR / "index.html"


def main():
    if not DATA_JSON.exists():
        print(f"❌ Не знайдено {DATA_JSON}")
        return False

    with open(DATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # --- Оновити EMBEDDED_DATA ---
    # Використовуємо маркери /* DATA_START */ та /* DATA_END */ для надійності
    embedded_json = json.dumps(data, ensure_ascii=False, indent=2)
    # Додати відступ для блоку даних
    lines = embedded_json.split("\n")
    indented = lines[0] + "\n" + "\n".join("      " + l for l in lines[1:])
    
    replacement = f"/* DATA_START */\n    const EMBEDDED_DATA = {indented};\n    /* DATA_END */"
    pattern = r"/\* DATA_START \*/.*?/\* DATA_END \*/"
    new_html, count = re.subn(pattern, replacement, html, flags=re.DOTALL)

    if count == 0:
        # Спробувати старий паттерн, якщо маркери ще не додані (на всяк випадок)
        pattern_old = r"const EMBEDDED_DATA = \[.*?\];"
        replacement_old = f"const EMBEDDED_DATA = {indented};"
        new_html, count = re.subn(pattern_old, replacement_old, html, flags=re.DOTALL)
        
        if count == 0:
            print("❌ Не знайдено EMBEDDED_DATA або маркерів в index.html")
            return False

    # --- Оновити дату ---
    today = datetime.now().strftime("%d.%m.%Y")
    new_html = re.sub(
        r"Станом на [\d.]+",
        f"Станом на {today}",
        new_html,
    )

    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"✅ index.html оновлено з data.json (дата: {today})")
    return True


if __name__ == "__main__":
    main()
