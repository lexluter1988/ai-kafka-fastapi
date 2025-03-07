import json
import logging
import sys
from logging.config import dictConfig

import structlog

from app.settings import Settings


class CustomJSONFormatter(logging.Formatter):
    def __call__(self, logger, name, event_dict):
        return json.dumps(event_dict, ensure_ascii=False)


def setup_logging(settings: Settings):
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': CustomJSONFormatter,
            },
        },
        'handlers': {
            'default': {
                'level': settings.log_level,
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': settings.log_format,
            },
        },
        'root': {'handlers': ['default'], 'level': 'INFO'},
        'loggers': {
            'uvicorn': {'handlers': ['default'], 'level': 'INFO', 'propagate': False},
            'uvicorn.access': {'handlers': ['default'], 'level': 'INFO', 'propagate': False},
            'uvicorn.error': {'handlers': ['default'], 'level': 'INFO', 'propagate': False},
            'fastapi': {'handlers': ['default'], 'level': 'INFO', 'propagate': False},
            'aiokafka': {'handlers': ['default'], 'level': 'WARNING', 'propagate': False},
            'kafka': {'handlers': ['default'], 'level': 'WARNING', 'propagate': False},
            'asyncio': {'handlers': ['default'], 'level': 'WARNING', 'propagate': False},
        },
    }

    dictConfig(log_config)

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.JSONRenderer(ensure_ascii=False),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger()
