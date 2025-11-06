import { postJSON } from '/static/utils.js';

let grid = [["","",""],["","",""],["","",""]];
let player = "X";
let gameOver = false;

const table = document.getElementById("grid");
const messageDiv = document.getElementById("message");
const resetBtn = document.getElementById("resetBtn");

function renderGrid() {
  table.innerHTML = "";
  for (let y = 0; y < 3; y++) {
    const row = document.createElement("tr");
    for (let x = 0; x < 3; x++) {
      const cell = document.createElement("td");
      cell.textContent = grid[y][x];
      cell.onclick = () => play(y, x);
      row.appendChild(cell);
    }
    table.appendChild(row);
  }
}

async function play(row, col) {
  if (grid[row][col] !== "" || gameOver) return;

  const data = await postJSON("/play/local", { grid, player, row, col });
  grid = data.grid;
  player = data.next_player;
  gameOver = data.next_player === null;
  messageDiv.textContent = data.message || "";
  renderGrid();
}

async function resetGame() {
  const data = await postJSON("/play/reset", {});
  grid = data.grid;
  player = data.next_player;
  gameOver = false;
  messageDiv.textContent = "";
  renderGrid();
}

resetBtn.onclick = resetGame;
renderGrid();
