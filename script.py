import os
import re
import shutil

def parse_structured_output(text):
    """
    Parses the text for sections demarcated by lines like:
    --- HTML ---
    [content]
    --- INSTRUCTIONS ---
    [content]

    Returns a dict with keys = ["HTML", "CSS", "JS", "INSTRUCTIONS"] and values = block content.
    """
    keys = ["HTML", "INSTRUCTIONS"]
    parsed = {}

    for i, key in enumerate(keys):
        # If there's another key ahead, capture until that key
        if i < len(keys) - 1:
            next_key = keys[i + 1]
            # Capture all text from '--- key ---' up to the next '--- next_key ---'
            pattern = rf"--- {key} ---\s*(.*?)\s*(?=--- {next_key} ---)"
        else:
            # If it's the last key, capture until the end of the text
            pattern = rf"--- {key} ---\s*(.*)"

        match = re.search(pattern, text, re.DOTALL)
        if match:
            parsed[key] = match.group(1).strip()
        else:
            parsed[key] = ""

    return parsed

def save_parts(parsed, output_dir="game"):
    """
    Saves each parsed section to a separate file in `output_dir`.
    Expects the parsed dict to have keys: HTML, CSS, JS, INSTRUCTIONS
    """
    # If the directory exists, delete it and start fresh
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    file_map = {
        "HTML": "index.html",
        "INSTRUCTIONS": "instructions.txt"
    }

    for section, filename in file_map.items():
        code = parsed.get(section, "").strip()
        if code:
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            print(f"✅ Saved {section} to {filename}")
        else:
            print(f"⚠️ Skipped {section} — section is empty.")

if __name__ == "__main__":
    # Example usage: read from a file containing the generated output
    with open("output/generated_code.txt", "r", encoding="utf-8") as file:
        content = file.read()

    # Parse the structured text
    parsed_sections = parse_structured_output(content)

    # Save each block to its own file (index.html, style.css, game.js, instructions.txt)
    save_parts(parsed_sections)
