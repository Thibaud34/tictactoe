import httpx
from backend.config.settings import OLLAMA_URL
from backend.services.logger import logger

async def query_ollama(prompt: str, model: str = "llama3") -> str:
    """
    Interroge le modèle Ollama de manière asynchrone.
    Retourne la réponse brute (string), sans parsing JSON.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": model, "prompt": prompt}
            )
            response.raise_for_status()
            return response.text.strip()  # <- retour brut pour parsing robuste
    except Exception as e:
        logger.warning(f"Ollama fail ({model}): {e}")
        return ""  # réponse vide en cas d'erreur
