import os
from openai import OpenAI
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up Flask app
app = Flask(__name__)

# === Serve Game Files ===

# Serve index.html at the root (useful for direct visits)
@app.route('/')
def serve_index():
    return send_from_directory('game', 'index.html')

# Serve any file under /game/
@app.route('/game/<path:filename>')
def serve_game_file(filename):
    return send_from_directory('game', filename)

# === API Endpoint: Generate Game ===
@app.route('/generateGame', methods=['POST'])
def generate_game():
    data = request.get_json()
    user_prompt = data.get("prompt")
    if not user_prompt:
        return jsonify({"success": False, "error": "No prompt provided"}), 400

    system_prompt = ("""
        You are an Advanced Pygame Game Code Generator, creating engaging, visually impressive, and highly interactive games using only Pygame. The user will provide a simple or brief game idea.

        Your generated game must include:

        - A welcome page (loading page) clearly providing instructions on how to play, including which keys or inputs need to be pressed.
        - Robust design ensuring the game handles errors gracefully and remains stable during gameplay.
        - Quit and restart buttons accessible throughout gameplay.
        - Eye-catching visuals, dynamic animations, and smooth transitions.
        - Automatic generation of high-quality in-game images and sprites programmatically using Pygame's drawing capabilities, gradients, shapes, and textures.
        - An intuitive, responsive, and aesthetically pleasing UI/UX.
        - Engaging gameplay mechanics with clear and immediate user feedback.
        - Creative use of effects (particle systems, shadows, glow effects, parallax backgrounds).
        - A clear win/lose condition with engaging visual rewards or notifications.
        - Responsive and adaptive design suitable for various screen resolutions.

        Your response must strictly follow this structured, parseable format:

        --- PYTHON_CODE ---
        ```
        [Insert clean, executable Python code exclusively using Pygame here. Include no language tags or commentary.]
        ```

        --- HTML ---
        ```
        [Leave blank.]
        ```

        --- CSS ---
        ```
        [Leave blank.]
        ```

        --- JS ---
        ```
        [Leave blank.]
        ```

        --- INSTRUCTIONS ---
        ```
        [Provide clear, step-by-step instructions to:
        - Install Pygame via pip.
        - Run the game locally.
        - Briefly describe user interactions and gameplay.
        - Specify recommended Python version and compatibility notes, if any.]
        ```

        ⚠️ Do NOT include any songs or sound effects
        ⚠️ Do NOT include anything outside these 5 blocks.
        ⚠️ Do NOT include backtick language hints like ```python, ```html, etc.
        ⚠️ Do NOT explain the code or add commentary.

        This structured format will be parsed automatically, so strict adherence to formatting is essential."""
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=messages,
            temperature=0.3
        )

        generated_code = response.choices[0].message.content

        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        output_filepath = os.path.join(output_dir, "generated_code.txt")
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(generated_code)

        return jsonify({
            "success": True,
            "message": "Game code generated successfully.",
            "code": generated_code
        })

    except Exception as e:
        print("Error during code generation:", e)
        return jsonify({"success": False, "error": str(e)}), 500

# === Run App ===
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)
