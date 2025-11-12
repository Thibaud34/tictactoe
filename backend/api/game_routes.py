from asyncio.log import logger
from http.client import HTTPException
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.grid_manager import create_empty_grid, play_move
from services.game_logic import check_winner, next_player
from services.ai_service import ask_azure_for_move  
import asyncio
import json
from pathlib import Path

router = APIRouter()

last_grid = create_empty_grid(10)
game_over = False
winner = None
current_player = "X"

#path frontend
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

print(f"✅ FRONTEND PATH: {FRONTEND_DIR} | Exists: {FRONTEND_DIR.exists()}")
print("BASE_DIR:", BASE_DIR)
print("FRONTEND_DIR:", FRONTEND_DIR)
print("Static path exists:", (FRONTEND_DIR / "static").exists())

router.mount("/static", StaticFiles(directory=FRONTEND_DIR / "static"), name="static")

@router.get("/")
async def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")

@router.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "ok"}

@router.post("/play/local")
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

@router.post("/play/reset")
async def reset_game():
    global last_grid, game_over, winner, current_player
    last_grid = create_empty_grid(10)
    game_over = False
    winner = None
    current_player = "X"
    return {"grid": last_grid, "message": "Game reset", "next_player": "X"}

@router.post("/play/azure")
async def play_azure_vs_azure():
    global last_grid, game_over, winner, current_player
    last_grid = create_empty_grid(10)
    game_over = False
    winner = None
    current_player = "X"
    history = []

    while not game_over:
        move = ask_azure_for_move(last_grid, current_player)
        row, col = move.get("row"), move.get("col") if move else (0,0)
        last_grid = play_move(last_grid, col, row, current_player)
        winner = check_winner(last_grid, win_length=5)
        message = f"{current_player} joue ({row},{col})"
        if winner:
            game_over = True
            message = f"{winner} gagne !" if winner != "Draw" else "Match nul."
        history.append({"grid": [r.copy() for r in last_grid], "player": current_player, "message": message})
        if not game_over:
            current_player = next_player(current_player)
            await asyncio.sleep(0.2)
    return JSONResponse({"message": "🧠 IA joue...", "history": history})
