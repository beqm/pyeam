import logging

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
NOTSET = logging.NOTSET
DISABLED = 100000

DEFAULT_DATEFMT = "%Y/%m/%d %H:%M:%S"
DEFAULT_FMT = "%(asctime)s.%(msecs)03d %(name)s %(module)s::%(funcName)s %(levelname)s: %(message)s"


class Env:
    name: str = "app"

    @classmethod
    def init(cls, name: str = "app"):
        cls.name = name
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(DEFAULT_FMT, DEFAULT_DATEFMT))
        logging.getLogger(name).addHandler(handler)

        return cls
    
    @classmethod
    def __get_handler(cls, handler_type):
        logger = logging.getLogger(cls.name)
        for handler in logger.handlers:
            if isinstance(handler, handler_type):
                return handler
        return False

    @classmethod
    def level(cls, value: int):
        logging.getLogger(cls.name).setLevel(value)
        return cls
    
    @classmethod
    def file(cls, path: str, encoding: str = "utf-8"):
        if Env.__get_handler(logging.FileHandler):
            return cls
        
        file_handler = logging.FileHandler(path, encoding=encoding)
        file_handler.setFormatter(logging.Formatter(DEFAULT_FMT, DEFAULT_DATEFMT)) 
        logging.getLogger(cls.name).addHandler(file_handler)
        return cls

    @classmethod
    def fmt(cls, fmt: str | None = None, datefmt: str | None = None):
        handler = Env.__get_handler(logging.StreamHandler)
        if handler:
            handler.setFormatter(logging.Formatter(fmt or DEFAULT_FMT, datefmt or DEFAULT_DATEFMT))
            return cls

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt or DEFAULT_FMT, datefmt or DEFAULT_DATEFMT))
        logging.getLogger(cls.name).addHandler(handler)
        return cls
    
    
def info(msg: str):
    logging.getLogger(Env.name).info(msg, stacklevel=2)

def debug(msg: str):
    logging.getLogger(Env.name).debug(msg, stacklevel=2)

def warning(msg: str):
    logging.getLogger(Env.name).warning(msg, stacklevel=2)

def error(msg: str):
    logging.getLogger(Env.name).error(msg, stacklevel=2)

def critical(msg: str):
    logging.getLogger(Env.name).critical(msg, stacklevel=2)

