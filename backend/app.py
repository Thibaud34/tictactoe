from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from services.grid_manager import create_empty_grid, play_move
from services.game_logic import check_winner, next_player
from services.logger import logger

app = FastAPI(title="LLM Morpion API")

last_grid = create_empty_grid()
game_over = False
winner = None
current_player = "X"

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
    winner = check_winner(grid)
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
    last_grid = create_empty_grid()
    game_over = False
    winner = None
    current_player = "X"
    return {"grid": last_grid, "message": "Game reset", "next_player": "X"}

@app.get("/play/view", response_class=HTMLResponse)
async def view_grid():
    global last_grid, game_over, winner

    html = """
    <html>
    <head><title>TicTacToe</title>
    <style>
        table {border-collapse:collapse;font-size:30px;}
        td {width:60px;height:60px;text-align:center;border:1px solid black;cursor:pointer;}
        button {margin-top:10px;padding:5px 10px;font-size:16px;}
    </style></head><body>
    <h1>TicTacToe</h1>
    <div id="message">""" + (f"Game over: {winner}" if game_over else "") + """</div>
    <table id="grid">
    """
    for y, row in enumerate(last_grid):
        html += "<tr>"
        for x, cell in enumerate(row):
            html += f"<td onclick='play({y},{x})'>{cell}</td>"
        html += "</tr>"
    html += """
    </table>
    <button onclick="resetGame()">Recommencer</button>
    <script>
        let player = '""" + current_player + """';
        let grid = JSON.parse('""" + str(last_grid).replace("'", '"') + """');
        let gameOver = """ + str(game_over).lower() + """;

        function renderGrid() {
            const table = document.getElementById("grid");
            for (let y=0; y<3; y++) for (let x=0; x<3; x++)
                table.rows[y].cells[x].innerText = grid[y][x];
        }

        async function play(row, col) {
            if (grid[row][col] !== "" || gameOver) return;
            const res = await fetch('/play/local', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body: JSON.stringify({grid:grid, player:player, row:row, col:col})
            });
            const data = await res.json();
            grid = data.grid;
            player = data.next_player;
            gameOver = data.next_player === null;
            document.getElementById('message').innerText = data.message || '';
            renderGrid();
        }

        async function resetGame() {
            const res = await fetch('/play/reset', {method:'POST'});
            const data = await res.json();
            grid = data.grid;
            player = data.next_player;
            gameOver = false;
            document.getElementById('message').innerText = '';
            renderGrid();
        }
    </script>
    </body></html>
    """
    return HTMLResponse(content=html)
