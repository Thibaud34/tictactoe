def build_prompt(state: dict) -> str:
    """
    Construit une invite pour un modèle IA à partir de l'état du jeu.
    (ex : pour que l'IA joue automatiquement)
    """
    grid = state.get("grid", [])
    player = state.get("player", "X")
    return f"Grid: {grid}, Player: {player}"
