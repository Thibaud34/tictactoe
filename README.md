# Projet TicTacToc

Ceci est un projet de jeu TicTacToc avec IA intégrée.

## Prérequis
- Python 3.10+
- VS Code
- `uv` comme gestionnaire de paquets (`pip install uv`)

## Installation des dépendances
```bash
git clone < https://github.com/Thibaud34/tictactoe >
cd tictactoe
uv install
Lancer l'application
bash
Copier le code
uvicorn app:app --reload
--reload permet de recharger automatiquement le serveur à chaque modification du code.

Le serveur sera accessible sur http://127.0.0.1:8000.

Exemple d'utilisation
bash
Copier le code
curl -X POST "http://127.0.0.1:8000/play/local" \
  -H "Content-Type: application/json" \
  -d '{"grid":[["","",""],["","",""],["","",""]],"player":"X"}'