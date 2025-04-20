import os
import re
import shutil

def parse_structured_output(text):
    keys = ["PYTHON_CODE", "HTML", "CSS", "JS", "INSTRUCTIONS"]
    parsed = {}

    for key in keys:
        pattern = rf"--- {key} ---\s*```(?:\n)?(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        parsed[key] = match.group(1).strip() if match else ""

    return parsed

def save_parts(parsed, output_dir="output_game"):
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    file_map = {
        "PYTHON_CODE": "app.py",
        "HTML": "index.html",
        "CSS": "style.css",
        "JS": "game.js",
        "INSTRUCTIONS": "instructions.txt"
    }

    for section, filename in file_map.items():
        code = parsed.get(section, "").strip()
        if code:  # ✅ Only write file if there's content
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            print(f"✅ Saved {section} to {filename}")
        else:
            print(f"⚠️ Skipped {section} — section is empty.")

if __name__ == "__main__":
    with open("output/generated_code.txt", "r", encoding="utf-8") as file:
        content = file.read()

    parsed_sections = parse_structured_output(content)
    save_parts(parsed_sections)
