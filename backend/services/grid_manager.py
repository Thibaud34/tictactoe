
# from typing import List, Tuple

# Grid = List[List[str]]

# def create_empty_grid(size: int = 10) -> Grid:
#     """Crée une grille vide de taille donnée."""
#     return [["" for _ in range(size)] for _ in range(size)]

# def is_cell_empty(grid: Grid, x: int, y: int) -> bool:
#     """Vérifie si la cellule est libre."""
#     return grid[y][x] == ""

# def play_move(grid: Grid, x: int, y: int, player: str) -> Grid:
#     """Joue un coup si la cellule est vide, sinon renvoie la grille inchangée."""
#     if is_cell_empty(grid, x, y):
#         grid[y][x] = player
#     return grid
from typing import List

Grid = List[List[str]]

def create_empty_grid(size: int = 3) -> Grid:
    """Crée une grille vide de taille donnée."""
    return [["" for _ in range(size)] for _ in range(size)]

def is_cell_empty(grid: Grid, x: int, y: int) -> bool:
    """Vérifie si la cellule est libre."""
    return grid[y][x] == ""

def play_move(grid: Grid, x: int, y: int, player: str) -> Grid:
    """Joue un coup si la cellule est vide."""
    if is_cell_empty(grid, x, y):
        grid[y][x] = player
    return grid
