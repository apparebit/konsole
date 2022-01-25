"""
konsole: readable, pleasing console output

konsole is a simple logger built on top of Python's `logging` framework that
prints to standard error and, if the underlying terminal is amenable, does so
with the judicious use of bold and light type as well as a dash of color. This
package's interface stands on its own, no experience or direct interaction with
`logging` required. At the same time, this package plays equally well with other
loggers, just leave ~~konsole~~ 🙄 console output to it.
"""

from collections.abc import Iterator
from dataclasses import dataclass
import logging
import sys
import textwrap
from typing import Any, ContextManager, Optional, TextIO


__version__ = "0.1.0"

__all__ = [
    'init',
    'set_color',
    'set_level',
    'logger',
    'CRITICAL',
    'ERROR',
    'WARNING',
    'INFO',
    'DEBUG',
    'critical',
    'error',
    'warning',
    'info',
    'debug',
    'logger',
    'SGR',
    'ConsoleFormatter',
]


CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG


@dataclass(frozen=True)
class SGR:
    """
    The Select Graphic Rendition for enabling and disabling a style but without
    the prefix of escape character and opening square bracket '[' as well as the
    suffix of small letter 'm'.
    """

    on: str
    off: str

    def __call__(self, text: str) -> str:
        return f"\x1b[{self.on}m{text}\x1b[{self.off}m"


class ConsoleFormatter(logging.Formatter):
    """
    A log formatter targeting the console for human consumption. If supported by
    the terminal, this class uses indentation, bold and light type, as well as a
    dash of color to make log output look less busy and easier to read.
    """

    PUNCTUATION = ("!", ",", ".", ":", ";", "?", '"', "'")

    STYLE = {
        # Styles for level labels:
        "CRITICAL": SGR("1;35", "0;39"),
        "ERROR": SGR("1;31", "0;39"),
        "WARNING": SGR("1;38;5;208", "0;39"),
        "INFO": SGR("1", "0"),
        # Styles for other log entry components:
        "<message>": SGR("1", "0"),
        "<detail>": SGR("90", "0"),
        "<exception>": SGR("90", "0"),
    }

    def __init__(self, use_color: Optional[bool] = None) -> None:
        super().__init__("%(message)s")
        self.use_color = use_color if use_color is not None else sys.stderr.isatty()

    def applyStyle(self, name: str, text: str) -> str:
        style = self.STYLE.get(name)
        return style(text) if style and self.use_color else text

    def formatDetail(self, record: logging.LogRecord) -> str:
        detail = getattr(record, "detail", None)
        if detail is None:
            return ""

        lines: list[str] = []
        if isinstance(detail, dict):
            width = max(len(key) for key in detail)
            for key, value in detail.items():
                lines.append(f"\n    {key:>{width}} = {value}")
        elif isinstance(detail, (tuple, list)):
            for item in detail:
                lines.append(f"\n    {item}")
        else:
            lines.append(f"\n    {detail}")

        return self.applyStyle("<detail>", "".join(lines))

    def formatMessage(self, record: logging.LogRecord) -> str:
        levelname = self.applyStyle(record.levelname, f"[{record.levelname}]")
        message = super().formatMessage(record)
        detail = self.formatDetail(record)

        if not message.endswith(self.PUNCTUATION):
            # Ensure that message consistently ends with appropriate punctuation.
            message += ":" if detail or record.exc_info else "."
        if levelname[0] == "\x1b":
            # Only highlight message if level is highlighted too. Debug is just plain.
            message = self.applyStyle("<message>", message)
        if detail and record.exc_info:
            # Both detail and exception are formatted the same, need separating line.
            detail += "\n\n"

        return f"{levelname} {message}{detail}"

    def formatException(self, exc_info: Any) -> str:
        text = super().formatException(exc_info)
        text = textwrap.indent(text, "    ")
        return self.applyStyle("<exception>", text)


_formatter = ConsoleFormatter()
_handler = logging.StreamHandler()
_handler.setFormatter(_formatter)
_initialized = False


def init(*, level: int = INFO, use_color: Optional[bool] = None) -> None:
    """Initialize the logging system. Call this function first thing upon startup."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    if use_color is not None:
        _formatter.use_color = bool(use_color)

    logging.basicConfig(level=level, handlers=[_handler])
    logging.captureWarnings(True)


def set_color(use_color: bool) -> None:
    """Forcibly enable or disable colorful output."""
    init(use_color=use_color)
    _formatter.use_color = use_color


def set_level(level: int) -> None:
    """Set the minimum log level for emitting output."""
    init(level=level)
    logging.getLogger().setLevel(level)


def logger() -> logging.Logger:
    """Get the "`__main__`" logger for the application."""
    init()
    return logging.getLogger("__main__")


def critical(*args: Any, **kwargs: Any) -> None:
    """Emit a log message at fatal level."""
    logger().critical(*args, **kwargs)


def error(*args: Any, **kwargs: Any) -> None:
    """Emit a log message at error level."""
    logger().error(*args, **kwargs)


def warning(*args: Any, **kwargs: Any) -> None:
    """Emit a log message at warning level."""
    logger().warning(*args, **kwargs)


def info(*args: Any, **kwargs: Any) -> None:
    """Emit a log message at info level."""
    logger().info(*args, **kwargs)


def debug(*args: Any, **kwargs: Any) -> None:
    """Emit a log message at debug level."""
    logger().debug(*args, **kwargs)


def redirect(stream: TextIO) -> ContextManager[TextIO]:
    """
    Redirect konsole's output to the given stream. This function provides a
    functional alternative to `redirect_stderr` from Python's `contextlib`,
    which does not work for capturing the output of a `StreamHandler`. The
    context manager's `__enter__()` method returns the given stream, thus making
    it available in the `with` statement body as well.
    """
    init()

    import contextlib

    @contextlib.contextmanager
    def redirect() -> Iterator[TextIO]:
        old_stream = _handler.setStream(stream)
        try:
            yield stream
        finally:
            if old_stream:
                _handler.setStream(old_stream)

    return redirect()
