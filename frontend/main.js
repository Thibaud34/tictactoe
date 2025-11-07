// import { postJSON } from '/static/utils.js';

// let grid = [];
// let player = "X";
// let gameOver = false;

// const table = document.getElementById("grid");
// const messageDiv = document.getElementById("message");
// const resetBtn = document.getElementById("resetBtn");

// function renderGrid() {
//   table.innerHTML = "";

//   for (let y = 0; y < grid.length; y++) {
//     const row = document.createElement("tr");

//     for (let x = 0; x < grid[y].length; x++) {
//       const cell = document.createElement("td");
//       cell.textContent = grid[y][x];

//       if (!grid[y][x] && !gameOver) {
//         cell.style.cursor = "pointer";
//         cell.onclick = () => play(y, x);
//       } else {
//         cell.style.cursor = "default";
//       }

//       row.appendChild(cell);
//     }
//     table.appendChild(row);
//   }
// }

// async function play(row, col) {
//   if (grid[row][col] !== "" || gameOver) return;

//   const data = await postJSON("/play/local", { grid, player, row, col });
//   grid = data.grid;
//   player = data.next_player;
//   gameOver = data.next_player === null;
//   messageDiv.textContent = data.message || "";
//   renderGrid();
// }

// async function resetGame() {
//   const data = await postJSON("/play/reset", {});
//   grid = data.grid;
//   player = data.next_player;
//   gameOver = false;
//   messageDiv.textContent = "";
//   renderGrid();
// }

// async function initGame() {
//   await resetGame();
// }

// resetBtn.onclick = resetGame;
// initGame();

import { postJSON } from '/static/utils.js';

let grid = [];
let player = "X";
let gameOver = false;
let isAutoPlaying = false;

const table = document.getElementById("grid");
const messageDiv = document.getElementById("message");
const resetBtn = document.getElementById("resetBtn");
const autoBtn = document.getElementById("autoBtn");

// ===================================================
// 🔁 Rendu dynamique de la grille
// ===================================================
function renderGrid() {
  table.innerHTML = "";

  for (let y = 0; y < grid.length; y++) {
    const row = document.createElement("tr");

    for (let x = 0; x < grid[y].length; x++) {
      const cell = document.createElement("td");
      cell.textContent = grid[y][x];

      if (!grid[y][x] && !gameOver && !isAutoPlaying) {
        cell.style.cursor = "pointer";
        cell.onclick = () => play(y, x);
      } else {
        cell.style.cursor = "default";
      }

      row.appendChild(cell);
    }
    table.appendChild(row);
  }
}

// ===================================================
// 🧩 Mode manuel (clic humain)
// ===================================================
async function play(row, col) {
  if (grid[row][col] !== "" || gameOver || isAutoPlaying) return;

  const data = await postJSON("/play/local", { grid, player, row, col });
  grid = data.grid;
  player = data.next_player;
  gameOver = data.next_player === null;
  messageDiv.textContent = data.message || "";
  renderGrid();
}

// ===================================================
// 🧠 Mode IA vs IA
// ===================================================
async function autoPlay() {
  isAutoPlaying = true;
  messageDiv.textContent = "🧠 IA vs IA en cours...";
  await resetGame();

  try {
    const res = await fetch("http://127.0.0.1:8000/play/auto", { method: "POST" });
    const data = await res.json();
    const history = data.history || [];

    for (let i = 0; i < history.length; i++) {
      grid = history[i].grid;
      messageDiv.textContent = history[i].message;
      renderGrid();
      await new Promise(r => setTimeout(r, 500)); // animation
    }

    messageDiv.textContent += " ✅ Partie terminée.";
  } catch (err) {
    messageDiv.textContent = "❌ Erreur lors de l'IA vs IA : " + err;
  } finally {
    isAutoPlaying = false;
    gameOver = true;
  }
}

// ===================================================
// ♻️ Réinitialisation
// ===================================================
async function resetGame() {
  const data = await postJSON("/play/reset", {});
  grid = data.grid;
  player = data.next_player;
  gameOver = false;
  messageDiv.textContent = "";
  renderGrid();
}

// ===================================================
// 🚀 Initialisation au chargement
// ===================================================
async function initGame() {
  await resetGame();
}

resetBtn.onclick = resetGame;
autoBtn.onclick = autoPlay;
initGame();

