from contextlib import redirect_stderr
from io import StringIO
import logging
import re

# konsole does not use a test runner such as pytest for two reasons: First,
# bringing in a major dependency for relatively little testing code seems
# overkill. Second, pytest in particular captures all console output itself and
# thus interferes with konsole's redirection of standard error.


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
        konsole.debug("detail", detail={})

    # Validate konsole output.
    actual, expected = prepare(buffer.getvalue())
    compare(actual, expected)
    assert actual == expected


ESC_SEQ = re.compile(r"\x1b\[(?P<code>\d+(?:;\d+)*)m")


def prepare(output: str) -> tuple[list[str], list[str]]:
    actual = re.sub(ESC_SEQ, "⊲\g<code>⊳", output).split("\n")

    # fmt: off
    s = Style("⊲", "⊳")
    expected = "".join([
        s.info("[INFO]"), s.space, s.message("fyi."), s.newline,
        s.error("[ERROR]"), s.space, s.message("bad!"),
        s.detail("\n    broken!"), s.newline,
        '[CRITICAL] big bad!', s.newline,
        '[WARNING] beware!', s.newline,
        '    665', s.newline,
        '[DEBUG] detail.', s.newline,
    ]).split("\n")
    # fmt: on

    return actual, expected


def compare(actual: list[str], expected: list[str]) -> None:
    # SGR is NOT part of konsole's public API!
    import konsole

    red = konsole.SGR("31", "39")
    green = konsole.SGR("32", "39")

    for actual_line, expected_line in zip(actual, expected):
        if actual_line == expected_line:
            print("  " + actual_line)
        else:
            print(red("- " + actual_line))
            print(green("+ " + expected_line))


# Helper class to keep expected output readable by independently applying styles.
class Style:
    newline = "\n"
    space = " "

    def __init__(self, pre: str = "\x1b[", post: str = "m") -> None:
        self.pre = pre
        self.post = post

    def critical(self, _s_: str) -> str:
        return f"{self.pre}1;35{self.post}{_s_}{self.pre}0;39{self.post}"

    def detail(self, _s_: str) -> str:
        return f"{self.pre}90{self.post}{_s_}{self.pre}0{self.post}"

    def error(self, _s_: str) -> str:
        return f"{self.pre}1;31{self.post}{_s_}{self.pre}0;39{self.post}"

    def exception(self, _s_: str) -> str:
        return f"{self.pre}90{self.post}{_s_}{self.pre}0{self.post}"

    def info(self, _s_: str) -> str:
        return f"{self.pre}1{self.post}{_s_}{self.pre}0{self.post}"

    def message(self, _s_: str) -> str:
        return f"{self.pre}1{self.post}{_s_}{self.pre}0{self.post}"

    def warning(self, _s_: str) -> str:
        return f"{self.pre}1;38;5;208{self.post}{_s_}{self.pre}0;39{self.post}"


if __name__ == "__main__":
    test_konsole()
