from logging.config import dictConfig
from storeapi.config import config,DevConfig
def configure_logging()->None:
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        "filters":{
            "correlation_id": {
                "()": "asgi_correlation_id.CorrelationIdFilter",
                "uuid_length": 8 if isinstance(config,DevConfig) else 32,
                "default_value": "-",
            }
        },
        'formatters': {
            "console":{
                "class":"logging.Formatter",
                'datefmt': "%Y-%m-%d %H:%M:%S",
                "format":"%(correlation_id)s | %(asctime)s - %(name)s - %(lineno)d- %(message)s"
            },
            "file":{
                "class":"logging.Formatter",
                'datefmt': "%Y-%m-%d %H:%M:%S",
                "format":"%(correlation_id)s | %(asctime)s | %(name)s | %(lineno)d |%(message)s"
            }
        },
        'handlers':{
            "default": {
                "class":"logging.StreamHandler",
                "formatter":"console",
                "level":"DEBUG",
                "filters":["correlation_id"],
            },
            "rotating_file": {
                "class":"logging.handlers.RotatingFileHandler",
                "formatter":"file",
                "level":"DEBUG" if isinstance(config,DevConfig) else "INFO",
                "filename":"storeapi.log",
                "maxBytes": 1024 * 1024 ,
                "backupCount": 2,
                "encoding":"utf-8",
                "filters":["correlation_id"]
            },
        },
        'loggers': {
            "uvicorn": {
                "handlers":["default","rotating_file"],
                "level": "INFO",
                "propagate":False
            },
            "storeapi": {
                "handlers":["default","rotating_file"],
                "level":"DEBUG" if isinstance(config,DevConfig) else "INFO",
                "propagate":False
            },
            "databases": {
                "handlers":["default"],
                "level":"WARNING",
                "propagate":False
            }
        },
    })