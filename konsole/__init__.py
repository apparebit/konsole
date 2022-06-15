"""
konsole: readable, pleasing console output

[konsole](https://github.com/apparebit/konsole) is a simple logger built on top
of Python's `logging` framework that prints to standard error and, if the
underlying terminal is amenable to it, does so with the judicious use of bold
and light type as well as a dash of color. This package's interface stands on
its own, no experience or direct interaction with `logging` required. At the
same time, this package plays equally well with other loggers, just leave
console output to it.
"""
from __future__ import annotations

import logging
import sys

from typing import Any, cast, Optional, TextIO, TYPE_CHECKING

__version__ = "0.7.0"

__all__ = [
    'config', 'logger',
    'CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG',
    'critical', 'error', 'warning', 'info', 'debug', 'log',
]


class _NoSuchValueType:
    pass


_NoSuchValue = _NoSuchValueType()
del _NoSuchValueType


CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG

VOLUME_TO_LEVEL = {
    -2: CRITICAL,
    -1: ERROR,
    0: WARNING,
    1: INFO,
    2: DEBUG,
}


# --------------------------------------------------------------------------------------


class SGR:
    """
    The Select Graphic Rendition (SGR) for enabling and disabling a style but
    without the prefix of escape character and opening square bracket '[' as
    well as the suffix of small letter 'm'. SGR are not expected to nest.
    """

    def __init__(self, on: str, off: str) -> None:
        self._on = on
        self._off = off

    def __call__(self, text: str) -> str:
        return f"\x1b[{self._on}m{text}\x1b[{self._off}m"


class KonsoleFormatter(logging.Formatter):
    """
    A log formatter targeting the console for human consumption. If supported by
    the terminal, this class uses indentation, bold and light type, as well as a
    dash of color to make log output look less busy and easier to read.
    """

    DETAIL = "<detail>"
    EXCEPTION = "<exception>"
    MESSAGE = "<message>"

    PUNCTUATION = ("!", ",", ".", ":", ";", "?", '"', "'")

    STYLE = {
        # Styles for level labels:
        "CRITICAL": SGR("1;35", "0;39"),
        "ERROR": SGR("1;31", "0;39"),
        "WARNING": SGR("1;38;5;208", "0;39"),
        "INFO": SGR("1", "0"),
        # Styles for other components of log entries:
        MESSAGE: SGR("1", "0"),
        DETAIL: SGR("90", "0"),
        EXCEPTION: SGR("90", "0"),
    }

    def __init__(self, use_color: Optional[bool] = None) -> None:
        super().__init__("%(message)s")
        self.use_color = use_color if use_color is not None else sys.stderr.isatty()

    def applyStyle(self, name: str, text: str) -> str:
        style = self.STYLE.get(name)
        return style(text) if style and self.use_color else text

    def formatDetail(self, record: logging.LogRecord) -> str:
        detail = getattr(record, "detail", _NoSuchValue)
        if detail is _NoSuchValue:
            return ""

        lines: list[str]
        if isinstance(detail, dict):
            width = max((len(key) for key in detail), default=0)
            lines = [f"\n    {key:>{width}} = {value}" for key, value in detail.items()]
        elif isinstance(detail, (list, tuple, set, frozenset)):
            lines = [f"\n    {item}" for item in detail]
        else:
            lines = [f"\n    {line}" for line in str(detail).split("\n")]

        text = "".join(lines)
        return self.applyStyle(self.DETAIL, text) if text else ""

    def formatMessage(self, record: logging.LogRecord) -> str:
        levelname = self.applyStyle(record.levelname, f"[{record.levelname}]")
        message = super().formatMessage(record)
        detail = self.formatDetail(record)

        if not message.endswith(self.PUNCTUATION):
            # Ensure that message consistently ends with appropriate punctuation.
            message += ":" if detail or record.exc_info else "."
        if levelname[0] == "\x1b":
            # Only highlight message if level is highlighted too. Debug is just plain.
            message = self.applyStyle(self.MESSAGE, message)
        if detail and record.exc_info:
            # Both detail and exception are formatted the same, need separating line.
            detail += "\n\n"

        return f"{levelname} {message}{detail}"

    def formatException(self, exc_info: Any) -> str:
        text = super().formatException(exc_info)
        text = "\n    ".join(text.split("\n"))
        return self.applyStyle(self.EXCEPTION, f"    {text}")


class KonsoleHandler(logging.StreamHandler):
    # Always dereference sys.stderr so that konsole's output is redirectable.

    @property  # type: ignore
    def stream(self) -> TextIO:  # type: ignore
        return sys.stderr

    @stream.setter
    def stream(self, stream: TextIO) -> None:
        pass


# --------------------------------------------------------------------------------------


# Instead of subclassing logging.Logger directly, we create the konsole logger
# as a subclass of the currently configured logger class. That way, konsole
# composes with other extensions to the logging framework. Since mypy doesn't
# handle this intermingling of types and values, we also define a more static
# view — while type checking.

if TYPE_CHECKING:
    Logger = logging.Logger
else:
    Logger = logging.getLoggerClass()


class KonsoleLogger(Logger):
    # Unfortunately, the various logging methods of logging.Logger directly call
    # into Logger._log() if isEnabledFor(LEVEL) and _log() does *not* accept
    # arbitrary keyword arguments. Hence adding support for the detail keyword
    # is a bit more involved than it should be.

    def critical(self, msg: object, *args: object, **kwargs: object) -> None:
        self.log(CRITICAL, msg, *args, **kwargs)

    def error(self, msg: object, *args: object, **kwargs: object) -> None:
        self.log(ERROR, msg, *args, **kwargs)

    def warning(self, msg: object, *args: object, **kwargs: object) -> None:
        self.log(WARNING, msg, *args, **kwargs)

    def info(self, msg: object, *args: object, **kwargs: object) -> None:
        self.log(INFO, msg, *args, **kwargs)

    def debug(self, msg: object, *args: object, **kwargs: object) -> None:
        self.log(DEBUG, msg, *args, **kwargs)

    def log(self, level: int, msg: object, *args: object, **kwargs: Any) -> None:
        if "detail" in kwargs:
            _prepare_detail(kwargs)
        super().log(level, msg, *args, **kwargs)


def _prepare_detail(kwargs: dict[str, object]) -> None:
    detail = kwargs.pop("detail")
    if "extra" not in kwargs:
        kwargs.update(extra={"detail": detail})
        return

    extra = kwargs["extra"]
    if not isinstance(extra, dict):
        raise ValueError(f'"extra" must be a dictionary but is "{extra}"!')

    extra.update(detail=detail)


# --------------------------------------------------------------------------------------


# Initialize konsole when this module is first imported by selectively changing
# the configuration of Python's logging module.

_formatter = KonsoleFormatter()
_handler = KonsoleHandler()
_handler.setFormatter(_formatter)
logging.setLoggerClass(KonsoleLogger)
_main_logger = cast(KonsoleLogger, logging.getLogger("__main__"))

logging.captureWarnings(True)
logging.getLogger().addHandler(_handler)
logging.getLogger().setLevel(INFO)


def config(
    *,
    level: Optional[int] = None,
    use_color: Optional[bool] = None,
    volume: Optional[int] = None,
) -> None:
    """
    Optionally set the logging level and forcibly enable or disable color.

    The volume argument provides a convenient alternative way of specifying the
    level — with larger volumes increasing the amount of information logged and
    zero corresponding to `WARNING`. If specified, the volume takes priority.
    """
    if isinstance(volume, int):
        level = VOLUME_TO_LEVEL[max(-2, min(volume, 2))]
    if level is not None:
        logging.getLogger().setLevel(level)
    if use_color is not None:
        _formatter.use_color = use_color


# --------------------------------------------------------------------------------------


def logger() -> logging.Logger:
    """Get the `__main__` application logger."""
    return _main_logger


def critical(msg: object, *args: object, **kwargs: object) -> None:
    """Log the given critical message."""
    _main_logger.log(CRITICAL, msg, *args, **kwargs)


def error(msg: object, *args: object, **kwargs: Any) -> None:
    """Log the given error message."""
    _main_logger.log(ERROR, msg, *args, **kwargs)


def warning(msg: object, *args: object, **kwargs: Any) -> None:
    """Log the given warning message."""
    _main_logger.log(WARNING, msg, *args, **kwargs)


def info(msg: object, *args: object, **kwargs: Any) -> None:
    """Log the given message."""
    _main_logger.log(INFO, msg, *args, **kwargs)


def debug(msg: object, *args: object, **kwargs: Any) -> None:
    """Log the given debug message."""
    _main_logger.log(DEBUG, msg, *args, **kwargs)


def log(level: int, msg: object, *args: object, **kwargs: Any) -> None:
    """Log the given message at the given level."""
    _main_logger.log(level, msg, *args, **kwargs)
