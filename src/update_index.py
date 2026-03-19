#!/usr/bin/env python3
"""Читає data.json і оновлює EMBEDDED_DATA та дату в index.html."""

import json
import re
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
    start_marker = "/* DATA_START */"
    end_marker = "/* DATA_END */"
    
    start_idx = html.find(start_marker)
    end_idx = html.find(end_marker)

    if start_idx != -1 and end_idx != -1:
        embedded_json = json.dumps(data, ensure_ascii=False, indent=2)
        # Додати відступ для блоку даних
        lines = embedded_json.split("\n")
        indented = lines[0] + "\n" + "\n".join("      " + l for l in lines[1:])
        
        replacement = f"const EMBEDDED_DATA = {indented};\n    "
        
        new_html = (
            html[:start_idx + len(start_marker)] + 
            "\n    " + replacement + 
            html[end_idx:]
        )
    else:
        # Спробувати старий паттерн, якщо маркери ще не додані
        pattern_old = r"const EMBEDDED_DATA = \[.*?\];"
        embedded_json = json.dumps(data, ensure_ascii=False, indent=2)
        lines = embedded_json.split("\n")
        indented = lines[0] + "\n" + "\n".join("      " + l for l in lines[1:])
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
