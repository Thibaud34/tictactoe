const localAPI = "http://127.0.0.1:8000/play/local";
const azureAPI = "http://127.0.0.1:8000/play/azure";

let grid = Array.from({ length: 10 }, () => Array(10).fill(""));
let joueur = "X";

const gridHTML = document.querySelector("#grid");
const messageDiv = document.querySelector("#message");
const resetBtn = document.querySelector("#resetBtn");
const aiBtn = document.querySelector("#aiBtn");

function viewGrid() {
    gridHTML.innerHTML = "";
    for (let y = 0; y < grid.length; y++) {
        const rowTr = document.createElement("tr");
        for (let x = 0; x < grid[y].length; x++) {
            const cellTd = document.createElement("td");
            cellTd.textContent = grid[y][x];
            cellTd.classList.add("cell");
            cellTd.dataset.row = y;
            cellTd.dataset.col = x;
            cellTd.addEventListener("click", () => playMove(y, x));
            rowTr.appendChild(cellTd);
        }
        gridHTML.appendChild(rowTr);
    }
}

function playMove(row, col) {
    if (grid[row][col] !== "") return;

    fetch(localAPI, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            grid: grid,
            player: joueur,
            row: row,
            col: col
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.grid) {
            grid = data.grid;
            joueur = data.next_player;
            viewGrid();
            messageDiv.textContent = data.message || "";
        }
    })
    .catch(err => console.error(err));
}

function playAIVsAI() {
    fetch(azureAPI, { method: "POST" })
    .then(res => res.json())
    .then(data => {
        if (data.history) {
            const last = data.history[data.history.length - 1];
            grid = last.grid;
            viewGrid();
            messageDiv.textContent = last.message;
        }
    })
    .catch(err => console.error(err));
}

resetBtn.addEventListener("click", () => {
    fetch("http://127.0.0.1:8000/play/reset", { method: "POST" })
    .then(res => res.json())
    .then(data => {
        grid = data.grid;
        joueur = data.next_player;
        viewGrid();
        messageDiv.textContent = data.message || "";
    });
});

aiBtn.addEventListener("click", playAIVsAI);

viewGrid();
