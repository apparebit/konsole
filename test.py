from __future__ import annotations
from contextlib import redirect_stderr
from io import StringIO
import logging
import re
import sys
import traceback
from typing import Callable

# konsole does not use a test runner such as pytest for two reasons: First,
# bringing in a major dependency for relatively little testing code seems
# overkill. Second, pytest in particular captures all console output itself and
# thus interferes with konsole's redirection of standard error.


if sys.stdout.isatty():
    def sgr(on: str, off: str) -> Callable[[str], str]:
        return lambda s: f"\x1b[{on}m{s}\x1b[{off}m"
else:
    def sgr(on: str, off: str) -> Callable[[str], str]:
        return lambda s: s

RED = sgr("31;1", "39;0")
GREEN = sgr("32;1", "39;0")


def test_konsole() -> None:
    # Validate pre-konsole-import configuration.
    vanilla_logger = logging.getLogger("vanilla_logger")
    assert not logging.getLogger().hasHandlers()
    assert logging.getLogger().level == logging.WARNING

    import konsole

    # Continue validating pre-konsole-import configuration.
    assert isinstance(vanilla_logger, logging.Logger)
    assert not isinstance(vanilla_logger, konsole.KonsoleLogger)

    # Validate post-konsole-import configuration.
    assert logging.getLogger().hasHandlers()
    assert logging.getLogger().level == konsole.INFO

    local_logger = logging.getLogger(__file__)
    assert isinstance(konsole.logger(), konsole.KonsoleLogger)
    assert isinstance(local_logger, konsole.KonsoleLogger)

    buffer = StringIO()
    with redirect_stderr(buffer):
        konsole.config(use_color=True)
        konsole.info("fyi")
        konsole.error("bad!", detail="broken!")

        konsole.config(use_color=False)
        konsole.critical("big %s!", "bad")
        konsole.debug("yo!")  # no output.

        konsole.config(level=konsole.DEBUG)
        local_logger.warning("beware!", detail=665)
        konsole.info("look", detail="one\ntwo")
        konsole.debug("detail", detail={})

    # Validate konsole output.
    actual, expected = prepare(buffer.getvalue())
    compare(actual, expected)
    assert actual == expected

    # Levels and volumes. NB: Current level is DEBUG.
    konsole.config(level=konsole.ERROR)
    assert logging.getLogger().level == konsole.ERROR
    konsole.config(level=konsole.ERROR, volume=2)
    assert logging.getLogger().level == konsole.DEBUG
    konsole.config(volume=-665)
    assert logging.getLogger().level == konsole.CRITICAL
    konsole.config(volume=665)
    assert logging.getLogger().level == konsole.DEBUG


ESC_SEQ = re.compile(r"\x1b\[(?P<code>\d+(?:;\d+)*)m")


def prepare(output: str) -> tuple[list[str], list[str]]:
    actual = re.sub(ESC_SEQ, "⊲\g<code>⊳", output).split("\n")

    # fmt: off
    space = " "
    newline = "\n"
    def sgr(on: str, s: str, off: str) -> str:
        return f"\x1b[{on}m{s}\x1b[{off}m"

    expected = re.sub(ESC_SEQ, "⊲\g<code>⊳", "".join([
        sgr("1", "[INFO]", "0"), space, sgr("1", "fyi.", "0"), newline,
        sgr("1;31", "[ERROR]", "0;39"), space, sgr("1", "bad!", "0"),
        sgr("90", "\n    broken!", "0"), newline,
        '[CRITICAL] big bad!', newline,
        '[WARNING] beware!', newline,
        '    665', newline,
        '[INFO] look:', newline,
        '    one', newline,
        '    two', newline,
        '[DEBUG] detail.', newline,
    ])).split("\n")
    # fmt: on

    return actual, expected


def compare(actual: list[str], expected: list[str]) -> None:
    for actual_line, expected_line in zip(actual, expected):
        if actual_line == expected_line:
            print("  " + actual_line)
        else:
            print(RED("- " + actual_line))
            print(GREEN("+ " + expected_line))


if __name__ == "__main__":
    try:
        test_konsole()
    except AssertionError as x:
        print(RED(str(x)))
    except Exception as x:
        print(RED(str(x)))
        print('\n'.join(traceback.format_exc()))
    else:
        print(GREEN("Happy, happy, joy, joy!"))
