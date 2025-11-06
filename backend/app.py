from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from loguru import logger

app = FastAPI(title="LLM Morpion API")

last_grid = [["","",""],["","",""],["","",""]]
game_over = False
winner = None

def check_winner(grid):
    # Lignes et colonnes
    for i in range(3):
        if grid[i][0] == grid[i][1] == grid[i][2] != "":
            return grid[i][0]
        if grid[0][i] == grid[1][i] == grid[2][i] != "":
            return grid[0][i]
    # Diagonales
    if grid[0][0] == grid[1][1] == grid[2][2] != "":
        return grid[0][0]
    if grid[0][2] == grid[1][1] == grid[2][0] != "":
        return grid[0][2]
    # Nulle
    if all(cell != "" for row in grid for cell in row):
        return "Draw"
    return None

@app.post("/play/local")
async def play_local(request: Request):
    global last_grid, game_over, winner
    if game_over:
        return {"grid": last_grid, "next_player": None, "message": f"Game over: {winner}"}

    try:
        try:
            data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON")

        grid = data.get("grid")
        player = data.get("player")
        row = data.get("row")
        col = data.get("col")

        if grid is None or player not in ["X","O"]:
            raise HTTPException(status_code=400, detail="Grid or player missing/invalid")

        if row is not None and col is not None:
            if grid[row][col] == "":
                grid[row][col] = player
            else:
                raise HTTPException(status_code=400, detail="Cell already occupied")

        next_player = "O" if player == "X" else "X"
        last_grid = grid

        # Vérifier victoire ou nulle
        winner = check_winner(grid)
        if winner:
            game_over = True
            message = "Draw!" if winner == "Draw" else f"{winner} wins!"
            next_player = None
        else:
            message = None

        return {"grid": grid, "next_player": next_player, "message": message}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erreur backend: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Nouveau endpoint pour réinitialiser la partie
@app.post("/play/reset")
async def reset_game():
    global last_grid, game_over, winner
    last_grid = [["","",""],["","",""],["","",""]]
    game_over = False
    winner = None
    return {"grid": last_grid, "message": "Game reset", "next_player": "X"}

@app.get("/play/view", response_class=HTMLResponse)
async def view_grid():
    global last_grid, game_over, winner
    html = """
    <html>
    <head>
    <title>TicTacToe</title>
    <style>
        table { border-collapse: collapse; font-size: 30px; }
        td { width: 60px; height: 60px; text-align: center; vertical-align: middle;
             border: 1px solid black; cursor: pointer; }
        button { margin-top: 10px; padding: 5px 10px; font-size: 16px; }
    </style>
    </head>
    <body>
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
    <button onclick="resetGame()">Recommencer la partie</button>
    <script>
        let player = "X";
        let grid = JSON.parse('""" + str(last_grid).replace("'", '"') + """');
        let gameOver = """ + str(game_over).lower() + """;

        function renderGrid() {
            const table = document.getElementById("grid");
            for (let y=0; y<3; y++) {
                for (let x=0; x<3; x++) {
                    table.rows[y].cells[x].innerText = grid[y][x];
                }
            }
        }

        async function play(row, col) {
            if (grid[row][col] !== "" || gameOver) return;

            const response = await fetch("/play/local", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({grid:grid, player:player, row:row, col:col})
            });
            const data = await response.json();
            grid = data.grid;
            player = data.next_player;
            gameOver = data.next_player === null;
            document.getElementById("message").innerText = data.message || "";
            renderGrid();
        }

        async function resetGame() {
            const response = await fetch("/play/reset", {method:"POST"});
            const data = await response.json();
            grid = data.grid;
            player = data.next_player;
            gameOver = false;
            document.getElementById("message").innerText = "";
            renderGrid();
        }
    </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
