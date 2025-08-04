# app/log_config.py

import logging
import sys

def setup_logging(level: str = "DEBUG"):
    """
    Konfiguruje logger aplikacji Flask.
    Logi są wypisywane do konsoli.
    """
    logger = logging.getLogger()
    logger.setLevel(level.upper())

    # Czyści istniejące handlery (np. z Jupyter lub testów)
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
