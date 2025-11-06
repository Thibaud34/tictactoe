from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from services.grid_manager import create_empty_grid, play_move
from services.game_logic import check_winner, next_player
from services.logger import logger

app = FastAPI(title="LLM Morpion API")

# Variables d'état
last_grid = create_empty_grid(10)
game_over = False
winner = None
current_player = "X"

# Serve frontend
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
async def serve_frontend():
    return FileResponse(frontend_path / "index.html")


@app.get("/health")
async def health_check():
    logger.info("Health check called")
    return {"status": "ok"}


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

    # Joue le coup
    grid = play_move(grid, col, row, player)
    last_grid = grid

    # Vérifie le gagnant
    winner = check_winner(grid, win_length=5)
    if winner:
        game_over = True
        message = "Draw!" if winner == "Draw" else f"{winner} wins!"
        next_p = None
    else:
        message = ""
        current_player = next_player(player)
        next_p = current_player

    return {"grid": grid, "next_player": next_p, "message": message}


@app.post("/play/reset")
async def reset_game():
    global last_grid, game_over, winner, current_player
    last_grid = create_empty_grid(10)
    game_over = False
    winner = None
    current_player = "X"
    return {"grid": last_grid, "message": "Game reset", "next_player": "X"}
