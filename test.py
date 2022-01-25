from io import StringIO

import konsole
SGR = konsole.SGR

def test_konsole() -> None:
    konsole.init(use_color=True)

    buffer = StringIO()
    with konsole.redirect(buffer):
        konsole.info("fyi")
        konsole.error("bad!", extra={"detail": "really!"})
        konsole.set_color(False)
        konsole.fatal("big %s!", "bad")

    actual = buffer.getvalue().replace("\x1b", "ESC").split("\n")
    expected = (
        SGR("1", "0")("[INFO]") + " " + SGR("1", "0")("fyi.") + "\n"
        + SGR("1;31", "0;39")("[ERROR]") + " " + SGR("1", "0")("bad!")
        + SGR("90", "0")("\n    really!") + "\n"
        + "[CRITICAL] big bad!\n"
    ).replace("\x1b", "ESC").split("\n")

    red = SGR("31", "39")
    green = SGR("32", "39")

    for actual_line, expected_line in zip(actual, expected):
        if actual_line == expected_line:
            print("     " + actual_line)
        else:
            print(red("    -" + actual_line))
            print(green("    +" + expected_line))

if __name__ == "__main__":
    test_konsole()
