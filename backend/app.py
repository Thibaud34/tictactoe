from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from loguru import logger
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="LLM Morpion API")

# Stocke la dernière grille jouée
last_grid = [["","",""],["","",""],["","",""]]

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

@app.post("/play/local")
async def play_local(request: Request):
    global last_grid
    try:
        try:
            data = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid or empty JSON")

        grid = data.get("grid")
        player = data.get("player")
        row = data.get("row")
        col = data.get("col")

        if grid is None or player not in ["X","O"]:
            raise HTTPException(status_code=400, detail="Grid or player missing/invalid")

        # Si row/col fournis, joue à cet endroit
        if row is not None and col is not None:
            if grid[row][col] == "":
                grid[row][col] = player
            else:
                raise HTTPException(status_code=400, detail="Cell already occupied")
        else:
            # Sinon joue le premier coup libre
            for y, r in enumerate(grid):
                for x, cell in enumerate(r):
                    if cell == "":
                        grid[y][x] = player
                        break

        # Détermine le prochain joueur
        next_player = "O" if player == "X" else "X"

        # Met à jour la grille pour /play/view
        last_grid = grid
        return {"grid": grid, "next_player": next_player}

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erreur backend: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/play/view", response_class=HTMLResponse)
async def view_grid():
    """
    Affiche la grille interactive en HTML
    """
    global last_grid
    html = """
    <html>
    <head>
    <title>TicTacToe</title>
    <style>
        table { border-collapse: collapse; font-size: 30px; }
        td { width: 60px; height: 60px; text-align: center; vertical-align: middle;
             border: 1px solid black; cursor: pointer; }
    </style>
    </head>
    <body>
    <h1>TicTacToe</h1>
    <table id="grid">
    """
    for y, row in enumerate(last_grid):
        html += "<tr>"
        for x, cell in enumerate(row):
            html += f"<td onclick='play({y},{x})'>{cell}</td>"
        html += "</tr>"
    html += """
    </table>
    <script>
        let player = "X";
        let grid = JSON.parse('""" + str(last_grid).replace("'", '"') + """');

        function renderGrid() {
            const table = document.getElementById("grid");
            for (let y=0; y<3; y++) {
                for (let x=0; x<3; x++) {
                    table.rows[y].cells[x].innerText = grid[y][x];
                }
            }
        }

        async function play(row, col) {
            if (grid[row][col] !== "") return;

            const response = await fetch("/play/local", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({grid:grid, player:player, row:row, col:col})
            });
            const data = await response.json();
            grid = data.grid;
            player = data.next_player;
            renderGrid();
        }
    </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
