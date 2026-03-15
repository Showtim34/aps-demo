"""Configuration de logging très légère pour le projet de démonstration.

La bibliothèque standard Python fournit déjà un système de logs robuste. Pour
un projet pédagogique, cela suffit et évite d'ajouter une dépendance.
"""

import logging
from logging.config import dictConfig


def configure_logging(debug: bool) -> None:
    """Configure un logger console global."""
    level = "DEBUG" if debug else "INFO"
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                }
            },
            "root": {"handlers": ["console"], "level": level},
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Retourne un logger au niveau module.

    Pattern d'usage :

    ```python
    logger = get_logger(__name__)
    ```
    """

    return logging.getLogger(name)
