import sys
from pathlib import Path
from loguru import logger
from config.settings import settings

# Ensure log directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "test_execution.log"

# Clear default handler to reconfigure custom enterprise formatting
logger.remove()

# Add standard console output handler
logger.add(
    sys.stdout,
    colorize=True,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    level=settings.LOG_LEVEL,
)

# Add structured file rotation handler
logger.add(
    LOG_FILE,
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.LOG_LEVEL,
)


class TestLogger:
    """Enterprise wrapper providing semantic logging helpers for UI automation actions."""

    @staticmethod
    def info(message: str) -> None:
        logger.info(message)

    @staticmethod
    def debug(message: str) -> None:
        logger.debug(message)

    @staticmethod
    def warning(message: str) -> None:
        logger.warning(message)

    @staticmethod
    def error(message: str) -> None:
        logger.error(message)

    @staticmethod
    def click(element_name: str) -> None:
        logger.info(f"[CLICK] Clicking on '{element_name}'")

    @staticmethod
    def input(field_name: str, value: str, mask: bool = False) -> None:
        display_val = "******" if mask else value
        logger.info(f"[INPUT] Typing '{display_val}' into '{field_name}'")

    @staticmethod
    def navigate(url: str) -> None:
        logger.info(f"[NAVIGATE] Navigating to URL: '{url}'")

    @staticmethod
    def verify(description: str) -> None:
        logger.info(f"[VERIFY] Asserting condition: '{description}'")

    @staticmethod
    def step(step_name: str) -> None:
        logger.info(f"[STEP] >>> {step_name} <<<")


log = TestLogger()

