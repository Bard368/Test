import logging
from rich.logging import RichHandler

def setup_logger():
    """Налаштовує логер з використанням бібліотеки rich для красивого виводу."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True)]
    )
    return logging.getLogger("agent_logger")

logger = setup_logger()