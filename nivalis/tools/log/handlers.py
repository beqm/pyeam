import json
import logging
import datetime as dt

class Colors:
    DEBUG = "\033[94m"
    INFO = "\033[92m"
    WARNING = "\033[93m"
    ERROR = "\033[91m"
    CRITICAL = "\033[95m"
    EXCEPTION = "\033[95m"
    RESET = "\033[0m"

RECORD_DEFAULTS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}

DEFAULT_JSON_FMT = {
    "asctime": "timestamp",
    "name": "name",
    "module": "module",
    "funcName": "function",
    "levelname": "level",
    "message": "message",
    "pathname": "path",
    "lineno": "line"
}

class JSONFormatter(logging.Formatter):
    def __init__(self, json_fmt=None, iso: bool = False):
        super().__init__()
        self.iso = iso
        self.json_fmt = json_fmt or DEFAULT_JSON_FMT


    def format(self, record):
        log_record = {}

        for k, v in self.json_fmt.items():
            if k == "asctime":
                log_record[v] = self.formatTime(record, self.datefmt)
                if self.iso:
                    log_record[v] = format_to_iso(record.created)
            elif k == "message":
                log_record[v] = record.getMessage()
            else:
                log_record[v] = getattr(record, k, None)

        if record.exc_info is not None:
            log_record["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            log_record["stack_info"] = self.formatStack(record.stack_info)

        for key, val in record.__dict__.items():
            if key not in RECORD_DEFAULTS:
                log_record[key] = val

        return json.dumps(log_record)

class CustomFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, colored: bool = False, iso: bool = False):
        super().__init__(fmt, datefmt)
        self.colored = colored
        self.iso = iso

    def format(self, record):
        asctime = format_to_iso(record.created)

        message = super().format(record)
        
        if self.colored:
            levelname = record.levelname
            colored_levelname = f"{Colors.__dict__.get(levelname, '')}{levelname}{Colors.RESET}"
            message = message.replace(levelname, colored_levelname, 1)

        if self.iso:
            message = message.replace(record.asctime, asctime, 1)
        
        return message
    

def format_to_iso(timestamp: float):
    local_timezone = dt.datetime.now().astimezone().tzinfo

    return dt.datetime.fromtimestamp(timestamp, tz=local_timezone) \
        .replace(microsecond=int((timestamp % 1000) * 1000)) \
        .isoformat(timespec='milliseconds')