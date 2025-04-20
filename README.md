curl -X POST -H "Content-Type: application/json" \
-d '{"prompt": "Create a desktop-friendly RPG game featuring quick exploration, intuitive character leveling, collectible items, simplified interactive dialogues, and quest-based progression. Include visually appealing environments optimized for desktop devices."}' \
http://localhost:4000/generateGame

uv run script.py

cd output_game && uv run app.py