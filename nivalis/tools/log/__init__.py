import queue
import logging
from typing import Dict, Optional
from nivalis.tools.log import handlers

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
NOTSET = logging.NOTSET
DISABLED = 100000

LIB_LOGGER = "nivalis"

DEFAULT_DATEFMT = "%d/%m/%Y %H:%M:%S"
DEFAULT_FMT = "%(asctime)s %(name)s %(levelname)s - %(message)s"


class Env:
    name: str = "app"
    _fmt: str | None = None
    _datefmt: str | None = None
    _iso: bool = False
    _colored: bool = False

    @classmethod
    def init(cls, name: str = "app"):
        cls.name = name
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        return cls
    
    @classmethod
    def __get_handler(cls, handler_type):
        logger = logging.getLogger(cls.name)
        for handler in logger.handlers:
            if isinstance(handler, handler_type):
                return handler
        return None

    @classmethod
    def level(cls, value: int):
        logging.getLogger(cls.name).setLevel(value)
        return cls
    
    @classmethod
    def fmt(cls, value: str):
        cls._fmt = value
        return cls
    
    @classmethod
    def datefmt(cls, value: int):
        cls._datefmt = value
        return cls
    
    @classmethod
    def colored(cls, value: bool = True):
        cls._colored = value
        return cls
    
    @classmethod
    def iso(cls, value: bool = True):
        cls._iso = value
        return cls
    
    @classmethod
    def file(cls, path: str, fmt: str | None = None, datefmt: str | None = None, 
             json: bool = False, json_fmt: Optional[Dict[str, str]] = None, encoding: str = "utf-8", iso: bool = False):
        
        logger = logging.getLogger(cls.name)
        file_handler = Env.__get_handler(logging.FileHandler)

        iso = iso or cls._iso
        fmt = fmt or cls._fmt or DEFAULT_FMT
        datefmt = datefmt or cls._datefmt or DEFAULT_DATEFMT

        formatter = handlers.CustomFormatter(fmt, datefmt, colored=False, iso=iso)

        if json:
            formatter = handlers.JSONFormatter(json_fmt=json_fmt, iso=iso)

        if file_handler:
            file_handler.setFormatter(formatter)
        else:
            stream_handler = logging.FileHandler(path, encoding=encoding)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
        
        return cls

    @classmethod
    def stdout(cls, fmt: str | None = None, datefmt: str | None = None, iso: bool = False, colored: bool = True):
        logger = logging.getLogger(cls.name)
        stream_handler = Env.__get_handler(logging.StreamHandler)

        iso = iso or cls._iso
        colored = colored or cls._colored
        fmt = fmt or cls._fmt or DEFAULT_FMT
        datefmt = datefmt or cls._datefmt or DEFAULT_DATEFMT

        formatter = handlers.CustomFormatter(fmt, datefmt, colored=colored, iso=iso)

        if stream_handler:
            stream_handler.setFormatter(formatter)
        else:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
        return cls
    
    @classmethod
    def queue(cls):
        from logging.handlers import QueueHandler, QueueListener
        logger = logging.getLogger(cls.name)
        
        if Env.__get_handler(QueueHandler):
            return cls
        
        cls.log_queue = queue.Queue()
        cls.queue_handler = QueueHandler(cls.log_queue)
        
        stream_handler = cls.__get_handler(logging.StreamHandler)
        file_handler = cls.__get_handler(logging.FileHandler)

        if stream_handler or file_handler:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
        
        logger.addHandler(cls.queue_handler)

        cls.queue_listener = QueueListener(cls.log_queue, *[handler for handler in [stream_handler, file_handler] if handler])
        cls.queue_listener.start()

        return cls
    
    def __del__(self):
        if hasattr(self, 'queue_listener') and self.queue_listener:
            self.queue_listener.stop()
    
def log(level: int, msg: str, *args, stacklevel=2, **kwargs):
    logging.getLogger(Env.name).log(level, msg, *args, stacklevel=kwargs.pop("stacklevel", stacklevel), **kwargs)
    
def info(msg: str, *args, stacklevel=2, **kwargs):
    logging.getLogger(Env.name).info(msg, *args, stacklevel=kwargs.pop("stacklevel", stacklevel), **kwargs)

def debug(msg: str, *args, stacklevel=2, **kwargs):
    logging.getLogger(Env.name).debug(msg, *args, stacklevel=kwargs.pop("stacklevel", stacklevel), **kwargs)

def warning(msg: str, *args, stacklevel=2, **kwargs):
    logging.getLogger(Env.name).warning(msg, *args, stacklevel=kwargs.pop("stacklevel", stacklevel), **kwargs)

def error(msg: str, *args, stacklevel=2, **kwargs):
    logging.getLogger(Env.name).error(msg, *args, stacklevel=kwargs.pop("stacklevel", stacklevel), **kwargs)

def exception(msg: str, *args, stacklevel=2, **kwargs):
    logging.getLogger(Env.name).exception(msg, *args, stacklevel=kwargs.pop("stacklevel", stacklevel), **kwargs)

def critical(msg: str, *args, stacklevel=2, **kwargs):
    logging.getLogger(Env.name).critical(msg, *args, stacklevel=kwargs.pop("stacklevel", stacklevel), **kwargs)

def get(name: str):
    return logging.getLogger(name)
    

def set_lib_level(level: int):
    logging.getLogger(LIB_LOGGER).setLevel(level)