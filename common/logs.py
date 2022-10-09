# * coding:utf-8 *


import logging
import sys
from pathlib import Path

from common.utils import Singleton
from loguru import logger

logLevel = {
    50: "CRITICAL",
    40: "ERROR",
    30: "WARNING",
    20: "INFO",
    10: "DEBUG",
    0: "NOTSET",
}

logSetting = {
    "filename": "fastapi.log",
    "level": "info",
    "rotation": "20 days",
    "retention": "1 months",
    "format": "<level>{level: <8}</level> "
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "request id: {extra[request_id]} - "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan> - "
    "<level>{message}</level>",
}


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = logLevel.get(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        _log = logger.bind(request_id="app")
        _log.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class Logger(metaclass=Singleton):
    def __init__(self):
        self.handler = InterceptHandler()
        self._path = None
        self._level = logSetting.get("level")
        self._filename = logSetting.get("filename")
        self._rotation = logSetting.get("rotation")
        self._retention = logSetting.get("retention")
        self._format = logSetting.get("format")
        self._init_path()

    def _init_path(self):
        if not self._path:
            p = Path(__file__).parent.parent.joinpath(Path("logs"))
            p.mkdir(exist_ok=True)
            self._path = p.joinpath(Path(self._filename))

    def make_logger(self):
        logger.remove()
        logger.add(
            sys.stdout,
            enqueue=True,
            backtrace=False,
            colorize=True,
            level=self._level.upper(),
            format=self._format,
        )
        logger.add(
            self._path,
            rotation=self._rotation,
            retention=self._retention,
            enqueue=True,
            backtrace=False,
            level=self._level.upper(),
            format=self._format,
        )
        logging.basicConfig(handlers=[self.handler], level=0)
        logging.getLogger("uvicorn.access").handlers = [self.handler]
        for _log in ["uvicorn", "uvicorn.error", "fastapi"]:
            _logger = logging.getLogger(_log)
            _logger.handlers = [self.handler]
        return logger.bind(request_id=None, method=None)
        # return logger.bind(request_id='app')

    def __call__(self, *args, **kwargs):
        return self.make_logger()


default_logger = Logger()()

if __name__ == "__main__":
    pass
