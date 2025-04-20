import os
from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from script import parse_structured_output, save_parts

# Load OpenAI key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
app.config['GENERATED_DIR'] = "game"
app.config['OUTPUT_FILE'] = "output/generated_code.txt"

# === HTML Template for Preview ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Generated Game Preview</title>
    <style>
        body { font-family: sans-serif; padding: 2em; background: #f9f9f9; }
        iframe { border: 1px solid #ccc; width: 100%; height: 607px; margin-bottom: 2em; }
        pre { background: #272822; color: #f8f8f2; padding: 1em; overflow-x: auto; border-radius: 6px; }
        label { font-weight: bold; display: block; margin-top: 1em; }
        form { background: white; padding: 2em; border-radius: 10px; box-shadow: 0 0 12px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <h1>Generated Game Preview</h1>
    <iframe src="/game/index.html"></iframe>

    <h2>Code Snippets</h2>
    <label>HTML:</label>
    <pre>{{ html }}</pre>
    
    <label>Instructions:</label>
    <pre>{{ instructions }}</pre>

    <h2>Try Another Prompt</h2>
    <form method="POST" action="/generateGame">
        <label for="prompt">Prompt:</label>
        <textarea name="prompt" rows="5" style="width:100%">{{ prompt }}</textarea>

        <label for="user_address">User Wallet Address:</label>
        <input type="text" name="user_address" style="width:100%" value="{{ user_address }}">

        <button type="submit" style="margin-top:1em;">Generate</button>
    </form>
</body>
</html>
"""

# === Routes ===

@app.route('/', methods=['GET'])
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>Generate Game</title></head>
    <body style="font-family:sans-serif; padding:2em;">
        <h1>Generate a Game</h1>
        <form method="POST" action="/generateGame">
            <label for="prompt">Prompt:</label><br>
            <textarea name="prompt" rows="6" cols="80"></textarea><br><br>

            <label for="user_address">Wallet Address:</label><br>
            <input type="text" name="user_address" size="60"><br><br>

            <button type="submit">Generate Game</button>
        </form>
    </body>
    </html>
    """)

@app.route('/generateGame', methods=['POST'])
def generate_game():
    prompt = request.form.get('prompt', '').strip()
    wallet_address = request.form.get('user_address', '').strip()

    if not prompt or not wallet_address:
        return "Error: Missing prompt or wallet address", 400

    full_prompt = prompt + f"\n\nWallet Address: {wallet_address}"

    # --- SYSTEM PROMPT ---
    system_prompt = ("""
        You are an Advanced HTML/CSS/JS Game Code Generator, creating engaging, visually impressive, and highly interactive games using only standard web technologies (HTML, CSS, and JavaScript). The user will provide a simple or brief game idea.

        Your generated game must include:

        A welcome (loading) page with clear instructions on how to play, including all required keys or inputs.

        Robust error handling ensuring the game remains stable during play.

        Quit and restart buttons that are accessible throughout gameplay.

        Eye-catching visuals, dynamic animations, and smooth transitions—all implemented via HTML/CSS/JS without external assets.

        Programmatically generated visuals (shapes, gradients, textures) in place of images or sprites—no external image files.

        An intuitive, responsive, and visually appealing user interface.

        Engaging gameplay mechanics with immediate feedback for user interactions.

        Creative effects (e.g., particle systems, shadows, glow effects, parallax backgrounds) to enhance immersion.

        A clear win/lose condition with a memorable final scene or notification.

        A responsive design that adapts to various screen resolutions and sizes.

        A points system where the user earns points throughout the game.

        A store where users can spend those points to claim a reward.

        A Flask-based blockchain reward system integration:

        The user can choose to spend points by providing a wallet address.

        Use fetch (or XHR) to send a POST request to an endpoint (e.g., http://127.0.0.1:5000/reward) with JSON containing the user’s address.

        Show user feedback (“Reward transaction sent!” or any error message) within the game UI.

        The expected JSON body must be:
        {
        "user_address": "0xUserAddress..."
        }
        Your response must strictly follow this exact structured format:
        --- HTML ---
        [Insert a single self-contained HTML document here (including any necessary CSS & JS).
        No external files or libraries allowed. No additional commentary or language hints.]

        --- INSTRUCTIONS ---
        [Step-by-step usage instructions:
        - How to open/run the HTML file locally
        - How gameplay works (briefly)
        - How to interact with the store and send the reward transaction
        - Recommended browser or version requirements

        No extra commentary beyond these instructions.]
        ⚠️ Prohibitions:

        No external libraries, no extra files.

        No inline explanations or descriptions outside the specified blocks.

        No sound effects or music.

        No code comments or debugging text in the output.

        No backtick language hints (e.g., ```html or ```javascript).

        This format will be parsed automatically, so maintaining the exact block delimiters and structure is critical."""
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": full_prompt}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=messages,
            temperature=0.3
        )

        generated_code = response.choices[0].message.content

        os.makedirs("output", exist_ok=True)
        with open(app.config['OUTPUT_FILE'], "w", encoding="utf-8") as f:
            f.write(generated_code)

        return redirect(url_for('preview', prompt=prompt, user_address=wallet_address))

    except Exception as e:
        print("OpenAI Error:", e)
        return f"OpenAI API Error: {e}", 500

@app.route('/preview')
def preview():
    with open(app.config['OUTPUT_FILE'], "r", encoding="utf-8") as f:
        content = f.read()

    parsed = parse_structured_output(content)
    save_parts(parsed, output_dir=app.config['GENERATED_DIR'])

    return render_template_string(HTML_TEMPLATE,
                                  html=parsed.get("HTML", "")[:],
                                  instructions=parsed.get("INSTRUCTIONS", ""),
                                  prompt=request.args.get("prompt", ""),
                                  user_address=request.args.get("user_address", ""))

@app.route('/game/<path:filename>')
def serve_game(filename):
    return send_from_directory(app.config['GENERATED_DIR'], filename)

# === Run App ===
if __name__ == '__main__':
    app.run(debug=True, port=5001)
