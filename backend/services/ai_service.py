from asyncio.log import logger
import os
import sys
import asyncio
import httpx
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import requests
from dotenv import load_dotenv
import os

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
AZURE_API_VERSION = "2024-12-01-preview"

def ask_azure_for_move(grid, player):
    prompt = f"""
    You are an expert Tic-Tac-Toe AI playing on a 10x10 grid.
    Your symbol is '{player}'.
    The goal is to connect 5 symbols in a row (horizontally, vertically, or diagonally).

    Here is the current grid:
    {json.dumps(grid)}

    ### Your objective
    - Always play the most strategic move possible.
    - Try to **win as fast as possible** if a winning move exists.
    - If no immediate win, try to **block your opponent** from winning.
    - If neither is possible, choose a position that helps you **create multiple future winning opportunities**.

    ### Rules
    - You can only play in empty cells ("").
    - Indices start at 0 (top-left = (0,0)).
    - The grid is 10x10.

    ### Response format
    Respond ONLY in **strict JSON** format:
    {{"row": <integer between 0 and 9>, "col": <integer between 0 and 9>}}

    ⚠️ Do not include any explanation, commentary, or text outside the JSON object.
    """
    url = f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version={AZURE_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY
    }
    payload = {
        "messages": [
            {"role": "system", "content": "You are a tic-tac-toe AI player."},
            {"role": "user", "content": prompt}
        ],
        "max_completion_tokens": 150,
    }

    print(f"[AZURE] Endpoint: {url}")
    print(f"[AZURE] Payload: {json.dumps(payload, indent=2)}")
 

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(response.status_code)
        data = response.json()
        print(data)
        content = data["choices"][0]["message"]["content"]
        move = json.loads(content)
        return move
    except Exception as e:
        logger.warning(f"Azure API error for player {player}: {e}")
        return None