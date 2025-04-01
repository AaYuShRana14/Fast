from logging.config import dictConfig
from storeapi.config import config,DevConfig
def configure_logging()->None:
    dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            "console":{
                "class":"logging.Formatter",
                'datefmt': "%Y-%m-%d %H:%M:%S",
                "format":"%(asctime)s - %(name)s - %(lineno)d- %(message)s"
            },
            "file":{
                "class":"logging.Formatter",
                'datefmt': "%Y-%m-%d %H:%M:%S",
                "format":"%(asctime)s | %(name)s | %(lineno)d |%(message)s"
            }
        },
        'handlers':{
            "default": {
                "class":"logging.StreamHandler",
                "formatter":"console",
                "level":"DEBUG"
            },
            "rotating_file": {
                "class":"logging.handlers.RotatingFileHandler",
                "formatter":"file",
                "level":"DEBUG" if isinstance(config,DevConfig) else "INFO",
                "filename":"storeapi.log",
                "maxBytes": 1024 * 1024 ,
                "backupCount": 2,
                "encoding":"utf-8",
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