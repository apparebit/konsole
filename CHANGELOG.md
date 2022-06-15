# konsole changelog

### v0.7.0 (15 Jun 2022):

  * Add support for `volume` argument to `config()` as convenient alternative to
    `level` argument for command line tools.

### v0.6.0 (29 Mar 2022):

  * After converting arbitrary detail values to strings, also split them into
    lines.
  * Ensure that type annotations are treated as strings, so that generic types
    do not trip up konsole in Python 3.7 or 3.8.

### v0.5.1 (7 Feb 2022):

  * Fix `__all__` to list only symbols that actually exist.

### v0.5.0 (7 Feb 2022):

  * Use custom logging handler to make output redirectable with `contextlib`'s
    `redirect_stderr`.
  * Remove the now superfluous `konsole.redirect()`.

### v0.4.0 (3 Feb 2022):

  * Fix unexpected exception upon detail being an empty dictionary.
  * More generally, improve handling of detail values that are effectively empty.
  * Fix indentation of first line of exception trace.
  * Add screenshot illustrating konsole's output to [project readme](README.md)

### v0.3.0 (29 Jan 2022):

  * Initialize konsole eagerly on first import. Replace `init()` with `config()`.
  * Instead of replacing logging configuration with `basicConfig()`, augment
    current configuration by adding handler to root logger and by replacing
    logger class with subclass.
  * Remove runtime dependencies on the standard library's `collections.abc`,
    `dataclasses`, and `textwrap` packages to reduce import latency and memory
    overhead.
  * Completely refactor test script, improve coverage.
  * Update documentation accordingly.

### v0.2.0 (26 Jan 2022):

  * Surface `detail` keyword argument for logging functions.
  * Document konsole's public API.
  * Correctly handle corner cases of `detail` being `None`,
    `set_color()` and `set_level()` calling `init()`.
  * Cache main logger and directly access flag to eliminate repeated, trivial
    function calls.

### v0.1.0: 25 Jan 2022

Initial release.
