# Automate P2E Game Generation

[![Watch the video](https://img.youtube.com/vi/C8SXq7PjnDk/0.jpg)](https://www.youtube.com/watch?v=C8SXq7PjnDk)

This project is a Flask-based web application that integrates:

AI Game Generation – Utilizes OpenAI’s GPT model to generate blockchain game code based on user prompts.

Blockchain Rewards – Interacts with a smart contract on Ethereum via Web3.py to reward users (tokens).

## Key Features
Automated P2E Game Generation: Generates structured, parseable code with specified features like a welcome page, error handling, animations, and points/smart-contract integration.

Blockchain Integration: Uses a rewardUser function to send blockchain-based rewards to any provided address.

Flask Server: Routes for generating games (/generateGame), rewarding users (/reward), and serving game files.

Environment Management: All sensitive information is loaded from a .env file for security and Utilize python UV Package Manager for faster environment management.

## Run the model
```bash
uv run smart_contract.py
uv run app.py
```

Example prompt:
```
Prompt: Create a desktop-friendly Pet game where you can feed your pet and gain points. You should create a store where people can spend their points to earn money. Include visually appealing environments optimized for desktop devices.

user_address: <Your Account Address>
```
