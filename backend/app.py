import asyncio
import re
import random
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import requests
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.services.grid_manager import create_empty_grid, play_move
from backend.services.game_logic import check_winner, next_player
import json
from backend.services.logger import logger
from backend.models.ollama_client import query_ollama  # async
from backend.services.prompt_builder import build_tictactoe_prompt

# ============================================================
# Configuration FastAPI
# ============================================================

app = FastAPI(title="LLM Morpion API")

BASE_DIR = Path(__file__).resolve().parent.parent
frontend_path = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# ============================================================
# Variables globales
# ============================================================

last_grid = create_empty_grid(10)
game_over = False
winner = None
current_player = "X"

from dotenv import load_dotenv

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "o4-mini")
AZURE_API_VERSION = "2024-12-01-preview"
print("BASE_DIR:", BASE_DIR)
print("Frontend path:", frontend_path.exists())
print("Loaded AZURE_OPENAI_ENDPOINT:", AZURE_OPENAI_ENDPOINT)
print("Loaded AZURE_OPENAI_DEPLOYMENT_NAME:", AZURE_OPENAI_DEPLOYMENT_NAME)

# ============================================================
# Routes
# ============================================================

@app.get("/")
async def serve_frontend():
    """Retourne le fichier HTML principal"""
    return FileResponse(frontend_path / "index.html")

@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "ok"}

# ============================================================
# Mode humain
# ============================================================

@app.post("/play/local")
async def play_local(request: Request):
    global last_grid, game_over, winner, current_player

    if game_over:
        return {"grid": last_grid, "next_player": None, "message": f"Game over: {winner}"}

    data = await request.json()
    grid = data.get("grid")
    player = data.get("player")
    row = data.get("row")
    col = data.get("col")

    if grid is None or player not in ["X", "O"]:
        raise HTTPException(status_code=400, detail="Invalid grid or player")

    last_grid = play_move(grid, col, row, player)
    print(f"[LOCAL] Grid after move:\n{json.dumps(last_grid, indent=2)}")
    winner = check_winner(last_grid, win_length=5)
    print(f"[LOCAL] Winner check result: {winner}")

    if winner:
        game_over = True
        message = f"{winner} wins!" if winner != "Draw" else "Draw!"
        next_p = None
    else:
        current_player = next_player(player)
        message = ""
        next_p = current_player

    return {"grid": last_grid, "next_player": next_p, "message": message}

# ============================================================
# Réinitialisation
# ============================================================

@app.post("/play/reset")
async def reset_game():
    global last_grid, game_over, winner, current_player
    last_grid = create_empty_grid(10)
    game_over = False
    winner = None
    current_player = "X"
    return {"grid": last_grid, "message": "Game reset", "next_player": "X"}

def ask_azure_for_move(grid, player):
    """
    Appelle l'API Azure OpenAI pour obtenir un coup {row, col}.
    """
    prompt = f"""
    You are a tic-tac-toe AI playing on a 10x10 grid.
    Player {player} must play.
    Current grid:
    {json.dumps(grid)}
    Respond ONLY in JSON format: {{ "row": int, "col": int }}.
    
    You must respond strictly with JSON:
    {{
        "row": <integer between 0 and 9>,
        "col": <integer between 0 and 9>
    }}
    Do not add any text, commentary or explanation — only valid JSON.
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
        "max_completion_tokens": 150
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

# ----------------------
# Endpoint IA vs IA
# ----------------------
@app.post("/play/azure")
async def play_azure_vs_azure():
    global last_grid, game_over, winner, current_player

    # Reset
    last_grid = create_empty_grid(10)
    game_over = False
    winner = None
    current_player = "X"
    history = []

    print("[AZURE VS AZURE] Starting new match")
    print(f"[AZURE VS AZURE] Starting player: {current_player}")

    # while not game_over:
    #     move = ask_azure_for_move(last_grid, current_player)

    #     if move is None:
    #         # fallback si l'API échoue
    #         empty_cells = [(y, x) for y, row in enumerate(last_grid) for x, cell in enumerate(row) if cell == ""]
    #         if not empty_cells:
    #             break
    #         row, col = empty_cells[0]
    #     else:
    #         row, col = move.get("row"), move.get("col")
    #         if row is None or col is None or last_grid[row][col] != "" or not (0 <= row < 10) or not (0 <= col < 10):
    #             # coup invalide → fallback
    #             empty_cells = [(y, x) for y, row_ in enumerate(last_grid) for x, cell in enumerate(row_) if cell == ""]
    #             row, col = empty_cells[0]

    print("[AZURE VS AZURE] Starting new match")
    print(f"[AZURE VS AZURE] Starting player: {current_player}")

    while not game_over:
        print(f"[TURN] Player {current_player} thinking...")
        move = ask_azure_for_move(last_grid, current_player)
        print(f"[DEBUG] Type of move: {type(move)} | Value: {move}")
        row, col = move.get("row"), move.get("col")
        print(f"[TURN] Azure suggested: {move}")

        if move is None:
            print("[TURN] Azure returned None, fallback to first empty cell")
        else:
            print(f"[TURN] Move coordinates: row={move.get('row')}, col={move.get('col')}")

        print(f"[TURN] Grid before move:\n{json.dumps(last_grid, indent=2)}")

        last_grid = play_move(last_grid, col, row, current_player)
        print(f"[TURN] Grid after move:\n{json.dumps(last_grid, indent=2)}")

        winner = check_winner(last_grid, win_length=5)
        print(f"[TURN] Winner after move: {winner}")

        # Vérifier victoire
        winner = check_winner(last_grid, win_length=5)
        message = f"{current_player} joue ({row},{col})"
        if winner:
            game_over = True
            message = f"{winner} gagne !" if winner != "Draw" else "Match nul."

        # Historique pour frontend
        history.append({
            "grid": [r.copy() for r in last_grid],
            "player": current_player,
            "message": message
        })

        # Passage au joueur suivant
        if not game_over:
            current_player = next_player(current_player)
            await asyncio.sleep(0.2)  # animation frontend

    return JSONResponse({"history": history})