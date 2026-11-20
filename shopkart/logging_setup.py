"""One place to configure logging for the whole app."""
import logging.config
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"


def setup_logging(level="INFO"):
    LOG_DIR.mkdir(exist_ok=True)
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {"format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                       "datefmt": "%H:%M:%S"},
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "simple", "level": level},
            "file": {"class": "logging.handlers.RotatingFileHandler", "formatter": "simple",
                     "filename": str(LOG_DIR / "shopkart.log"), "maxBytes": 1_048_576,
                     "backupCount": 3, "encoding": "utf-8", "level": "DEBUG"},
        },
        "loggers": {
            "shopkart": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
        },
    })
