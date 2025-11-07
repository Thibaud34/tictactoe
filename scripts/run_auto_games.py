import asyncio
import re
import random
from backend.services.grid_manager import create_empty_grid, play_move
from backend.services.game_logic import check_winner, next_player
from backend.services.prompt_builder import build_tictactoe_prompt
from backend.models.ollama_client import query_ollama
from backend.services.logger import logger

async def run_model_vs_model(model_X="phi3:3.8b", model_O="phi3:3.8b", size=10, win_len=5):
    grid = create_empty_grid(size)
    current_player = "X"
    game_over = False
    turn = 0

    logger.info(f"=== DÉBUT PARTIE {model_X} (X) vs {model_O} (O) ===")

    while not game_over:
        turn += 1
        print(f"\n--- Tour {turn} ({current_player}) ---")

        prompt = build_tictactoe_prompt(grid, current_player)
        model_name = model_X if current_player == "X" else model_O

        # Appel du modèle avec gestion des erreurs
        try:
            raw_response = await query_ollama(prompt, model=model_name)
            clean_response = raw_response.strip().splitlines()[0]  # garde première ligne
            match = re.findall(r'\d+', clean_response)
            if len(match) >= 2:
                row, col = int(match[0]), int(match[1])
            else:
                raise ValueError("Pas assez de coordonnées")
        except Exception as e:
            logger.warning(f"⚠️ Ollama fail ({current_player}): {e}\nRéponse brute: {raw_response}")
            # fallback : coup aléatoire
            empty = [(y, x) for y, r in enumerate(grid) for x, c in enumerate(r) if c == ""]
            if not empty:
                break
            row, col = random.choice(empty)

        # Joue le coup
        grid = play_move(grid, col, row, current_player)

        # Vérifie victoire ou match nul
        winner = check_winner(grid, win_len)
        if winner:
            game_over = True
            print(f"\n🏁 Fin de partie : {winner} gagne !" if winner != "Draw" else "\n🤝 Match nul !")
            logger.info(f"Résultat : {winner}")
            break

        current_player = next_player(current_player)
        await asyncio.sleep(0.2)

    print("\nGrille finale :")
    for r in grid:
        print(" ".join(c or "." for c in r))

if __name__ == "__main__":
    asyncio.run(run_model_vs_model())
