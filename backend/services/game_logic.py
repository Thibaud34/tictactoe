from typing import List, Optional

Grid = List[List[str]]

def check_winner(grid: Grid) -> Optional[str]:
    """Retourne 'X', 'O' si gagnant, 'Draw' si nul, sinon None."""
    size = len(grid)

    # Lignes et colonnes
    for i in range(size):
        if grid[i][0] and all(grid[i][j] == grid[i][0] for j in range(size)):
            return grid[i][0]
        if grid[0][i] and all(grid[j][i] == grid[0][i] for j in range(size)):
            return grid[0][i]

    # Diagonales
    if grid[0][0] and all(grid[i][i] == grid[0][0] for i in range(size)):
        return grid[0][0]
    if grid[0][size - 1] and all(grid[i][size - 1 - i] == grid[0][size - 1] for i in range(size)):
        return grid[0][size - 1]

    # Égalité
    if all(cell != "" for row in grid for cell in row):
        return "Draw"

    return None

def next_player(player: str) -> str:
    """Retourne le joueur suivant."""
    return "O" if player == "X" else "X"
