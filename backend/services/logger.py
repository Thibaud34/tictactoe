from loguru import logger
import sys

logger.remove()  # Nettoie les handlers par défaut
logger.add(sys.stdout, colorize=True, format="<green>{time}</green> <level>{message}</level>")
logger.add("logs/app.log", rotation="1 MB", level="INFO")

__all__ = ["logger"]
