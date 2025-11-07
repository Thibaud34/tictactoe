def build_tictactoe_prompt(grid, player):
    grid_text = "\n".join([" ".join(cell if cell else "." for cell in row) for row in grid])
    prompt = f"""
You are playing Tic-Tac-Toe on a 10x10 grid.
Your symbol is '{player}'.
Here is the current grid:
{grid_text}

Answer STRICTLY in JSON format like: {{"row": <number>, "col": <number>}}
Indices start at 0.
Do not write anything else, no explanations or extra text.
"""
    return prompt.strip()
