from loguru import logger
import sys


class LogConfig():
    _config = {
        "handlers": [
            {"sink": sys.stdout, "format": "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"},
            {"sink": "./.logs/raw.log", "format": "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
             "rotation": "100 MB", "retention": "1 week"},
            {"sink": "./.logs/serialized.log", "serialize": True},
        ]
    }

    def get_logging_config(self):
        return self._config
