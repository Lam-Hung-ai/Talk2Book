import logging
import os
from logging.handlers import TimedRotatingFileHandler

from app.core.config import settings

def setup_logging():

    level = getattr(logging, settings.logging.level.upper())
    handlers = []

    if settings.logging.output in ("console", "both"):
        handlers.append(logging.StreamHandler())

    log_path = os.path.join(settings.BACKEND_DIR, "log", "backend.log")
    if settings.logging.output in ("file", "both"):

        if settings.logging.file_path != "default":
            log_path = settings.logging.file_path
    
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        file_hander = TimedRotatingFileHandler(
            filename=log_path,
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
            utc=True
        )

        handlers.append(file_hander)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
        force=True
    ) 

    logging.getLogger(__name__).info(
        "Logging ready: level=%s, output=%s", level, log_path
    )