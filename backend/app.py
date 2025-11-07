# from fastapi import FastAPI, Request, HTTPException
# from fastapi.responses import FileResponse
# from fastapi.staticfiles import StaticFiles
# from pathlib import Path

# from services.grid_manager import create_empty_grid, play_move
# from services.game_logic import check_winner, next_player
# from services.logger import logger

# app = FastAPI(title="LLM Morpion API")

# # Variables d'état
# last_grid = create_empty_grid(10)
# game_over = False
# winner = None
# current_player = "X"

# # Serve frontend
# frontend_path = Path(__file__).parent.parent / "frontend"
# app.mount("/static", StaticFiles(directory=frontend_path), name="static")


# @app.get("/")
# async def serve_frontend():
#     return FileResponse(frontend_path / "index.html")


# @app.get("/health")
# async def health_check():
#     logger.info("Health check called")
#     return {"status": "ok"}


# @app.post("/play/local")
# async def play_local(request: Request):
#     global last_grid, game_over, winner, current_player

#     if game_over:
#         return {"grid": last_grid, "next_player": None, "message": f"Game over: {winner}"}

#     data = await request.json()
#     grid = data.get("grid")
#     player = data.get("player")
#     row = data.get("row")
#     col = data.get("col")

#     if grid is None or player not in ["X", "O"]:
#         raise HTTPException(status_code=400, detail="Invalid grid or player")

#     # Joue le coup
#     grid = play_move(grid, col, row, player)
#     last_grid = grid

#     # Vérifie le gagnant
#     winner = check_winner(grid, win_length=5)
#     if winner:
#         game_over = True
#         message = "Draw!" if winner == "Draw" else f"{winner} wins!"
#         next_p = None
#     else:
#         message = ""
#         current_player = next_player(player)
#         next_p = current_player

#     return {"grid": grid, "next_player": next_p, "message": message}


# @app.post("/play/reset")
# async def reset_game():
#     global last_grid, game_over, winner, current_player
#     last_grid = create_empty_grid(10)
#     game_over = False
#     winner = None
#     current_player = "X"
#     return {"grid": last_grid, "message": "Game reset", "next_player": "X"}

import asyncio
import re
import random
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.services.grid_manager import create_empty_grid, play_move
from backend.services.game_logic import check_winner, next_player
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
    winner = check_winner(last_grid, win_length=5)

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

# ============================================================
# Mode IA vs IA
# ============================================================

@app.post("/play/auto")
async def play_auto():
    """
    Mode IA vs IA : joue automatiquement jusqu'à victoire ou match nul.
    Utilise phi3:3.8b pour X et O.
    """
    global last_grid, game_over, winner, current_player

    # Réinitialisation
    last_grid = create_empty_grid(10)
    game_over = False
    winner = None
    current_player = "X"
    history = []

    while not game_over:
        # Génération du prompt pour l'IA (forcé JSON)
        prompt = build_tictactoe_prompt(last_grid, current_player)

        # Appel du modèle avec gestion d'erreurs
        try:
            model_output = await query_ollama(prompt, model="phi3:3.8b")
        except Exception as e:
            logger.warning(f"Ollama fail ({current_player}): {e}")
            model_output = ""

        import json

        try:
            coords = json.loads(model_output)
            row, col = coords["row"], coords["col"]
        except Exception:
            # fallback avec re.findall
            match = re.findall(r'\d+', model_output)
            if len(match) >= 2:
                row, col = int(match[0]), int(match[1])
            else:
                empty = [(y, x) for y, r in enumerate(last_grid) for x, c in enumerate(r) if c == ""]
                if not empty:
                    break
                row, col = empty[0]

        # Jouer le coup
        last_grid = play_move(last_grid, col, row, current_player)

        # Vérifier victoire ou match nul
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
