from typing import List, Optional

Grid = List[List[str]]

def check_winner(grid: Grid, win_length: int = 5) -> Optional[str]:
    """Retourne 'X' ou 'O' si un joueur a 5 alignés, 'Draw' si la grille est pleine, sinon None."""
    size = len(grid)

    def check_direction(y, x, dy, dx, player):
        """Vérifie s'il y a win_length symboles consécutifs depuis (y,x) dans la direction (dy,dx)."""
        count = 0
        for i in range(win_length):
            ny, nx = y + dy * i, x + dx * i
            if 0 <= ny < size and 0 <= nx < size and grid[ny][nx] == player:
                count += 1
            else:
                break
        return count == win_length

    for y in range(size):
        for x in range(size):
            player = grid[y][x]
            if player:
                if (
                    check_direction(y, x, 0, 1, player)    # → horizontal
                    or check_direction(y, x, 1, 0, player)  # ↓ vertical
                    or check_direction(y, x, 1, 1, player)  # ↘ diagonale principale
                    or check_direction(y, x, 1, -1, player) # ↙ diagonale inverse
                ):
                    return player

    # Vérifie si la grille est pleine = match nul
    if all(cell != "" for row in grid for cell in row):
        return "Draw"

    return None


def next_player(current: str) -> str:
    return "O" if current == "X" else "X"
