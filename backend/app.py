from fastapi import FastAPI
from loguru import logger

app = FastAPI(title="LLM Morpion API")

@app.get("/health")
async def health_check():
    """
    Endpoint de vérification du statut du backend.
    """
    logger.info("Health check called")
    return {"status": "ok", "message": "Backend is running"}
