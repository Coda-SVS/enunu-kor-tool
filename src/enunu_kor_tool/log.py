import os
import sys
import re
import inspect
import logging
import logging.handlers
import logging.config
from typing import Dict, Union, Callable

import colorlog
import tqdm


def unhandled_exception_hook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    get_logger(unhandled_exception_hook).critical("처리되지 않은 예외가 발생했습니다.", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = unhandled_exception_hook

DIR_PATH = "logs"


def get_logger(name: Union[str, Callable], logLevel: int = logging.INFO) -> logging.Logger:
    """로거를 생성합니다.

    Args:
        name (Union[str, Callable]): 로거 이름 또는 호출 함수
        logLevel (LogLevel, optional): 출력 로그 레벨. Default value is the value of SETTINGS.

    Returns:
        logging.Logger: 로거
    """

    global DIR_PATH

    if callable(name):
        frm = inspect.stack()[1]
        path = os.path.normpath(os.path.splitext(frm.filename)[0])
        module_path = path.split(os.sep)
        paths = []
        for path_name in reversed(module_path):
            if path_name == "ekt":
                break
            paths.append(path_name)
        paths.append(name.__name__)
        name = ".".join(paths)

    os.makedirs(DIR_PATH, exist_ok=True)

    if not logging.root.hasHandlers():
        root_logger_setup(DIR_PATH, logLevel)

    logger = logging.getLogger(name)
    logger.setLevel(logLevel)

    return logger


def get_default_config(dirpath: str, logLevel: int) -> Dict:
    using_root_handlers = ["console", "file", "warn_file"]

    get_fullname = lambda c: c.__qualname__ if (module := c.__module__) == "builtins" else module + "." + c.__qualname__

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "dest_console_filter": {
                "()": get_fullname(HandlerDestFilter),
            },
            "dest_file_filter": {
                "()": get_fullname(HandlerDestFilter),
            },
            "warn_dest_file_filter": {
                "()": get_fullname(HandlerDestFilter),
                "logLevel": logging.WARNING,
            },
        },
        "formatters": {
            "detail": {
                "format": "%(asctime)s %(levelname)-8s [%(name)s] [%(thread)d][%(filename)s:%(lineno)d] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "colored_console": {
                "()": get_fullname(colorlog.ColoredFormatter),
                "format": "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s [%(name)s] [%(thread)d][%(filename)s:%(lineno)d] %(log_color)s%(message)s%(reset)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "log_colors": {
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "bold_red",
                    "CRITICAL": "bold_red,bg_white",
                },
            },
        },
        "handlers": {
            "console": {
                "()": get_fullname(ConsoleLoggingHandler),
                "formatter": "colored_console",
                "filters": ["dest_console_filter"],
                "useTqdm": True,
            },
            "file": {
                "()": get_fullname(logging.handlers.TimedRotatingFileHandler),
                "formatter": "detail",
                "filters": ["dest_file_filter"],
                "filename": os.path.join(dirpath, "output.log"),
                # "maxBytes": 20 * 1024 * 1024,  # 20MB
                "when": "H",
                "interval": 6,
                "backupCount": 20,
                "encoding": "utf-8",
            },
            "warn_file": {
                "()": get_fullname(logging.handlers.TimedRotatingFileHandler),
                "formatter": "detail",
                "filters": ["warn_dest_file_filter"],
                "filename": os.path.join(dirpath, "error.log"),
                # "maxBytes": 20 * 1024 * 1024,  # 20MB
                "when": "H",
                "interval": 6,
                "backupCount": 30,
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": logging.getLevelName(logLevel),
            "handlers": using_root_handlers,
        },
    }

    return config


def root_logger_setup(dirpath: str, logLevel: int):
    config = get_default_config(dirpath, logLevel)
    logging.config.dictConfig(config)


# 출처: https://stackoverflow.com/a/38739634/12745351
# 수정해서 사용함
class ConsoleLoggingHandler(logging.StreamHandler):
    def __init__(self, useTqdm: bool = True):
        super().__init__()
        self._use_tqdm = useTqdm

    def emit(self, record):
        if self._use_tqdm:
            try:
                msg = self.format(record)
                tqdm.tqdm.write(msg)
                self.flush()
            except Exception:
                self.handleError(record)
        else:
            super().emit(record)


class HandlerDestFilter(logging.Filter):
    LINE_FORMATTER_REGEX = re.compile(r"\n(?!\t-> )")

    def __init__(self, name: str = "", logLevel: int = logging.NOTSET) -> None:
        super().__init__(name)
        self.log_level = logLevel

    def filter(self, record: logging.LogRecord):
        if record.levelno < self.log_level:
            return False

        self._format_line(record=record)
        return True

    def _format_line(self, record: logging.LogRecord):
        if not isinstance(record.msg, str):
            record.msg = str(record.msg)
        record.msg = self.LINE_FORMATTER_REGEX.sub("\n\t-> ", record.msg)
