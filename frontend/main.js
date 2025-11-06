const urlAPI = "http://127.0.0.1:8000/play/local";

let grid = [
    ["", "", ""],
    ["", "", ""],
    ["", "", ""]
];

let joueur = "X";

const gridHTML = document.querySelector("#grid");
const playButton = document.querySelector("#play");

function viewGrid() {
    gridHTML.innerHTML = "";
    for (let ligne of grid) {
        for (let cell of ligne) {
            const cellHTML = document.createElement("div");
            cellHTML.classList.add("cell");
            cellHTML.textContent = cell;
            gridHTML.appendChild(cellHTML);
        }
    }
}

playButton.addEventListener("click", () => {
    // Vérifie que la grille est bien un tableau avant envoi
    if (!Array.isArray(grid)) {
        console.error("Erreur : grille invalide.");
        return;
    }

    fetch(urlAPI, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            grid: grid,
            player: joueur
        })
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    })
    .then(data => {
        if (data.grid) {
            grid = data.grid;
            joueur = data.next_player;
            viewGrid();
        } else {
            console.error("Réponse invalide:", data);
        }
    })
    .catch(err => console.error("Erreur:", err));
});

// Affiche la grille au chargement
viewGrid();
