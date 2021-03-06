# konsole: readable, pleasing console output

> When you are writing a Python command line tool and your head is on fire
> because of overly rich frameworks that just don’t click.

![An interactive Python session using
konsole](https://raw.githubusercontent.com/apparebit/konsole/boss/session.png)

[konsole](https://github.com/apparebit/konsole) is a simple logger built on top
of Python's `logging` framework that prints to standard error and, if the
underlying terminal is amenable to it, does so with the judicious use of bold
and light type as well as a dash of color. This package's interface stands on
its own, no experience or direct interaction with `logging` required. At the
same time, this package plays equally well with other loggers, just leave
~~konsole~~ 🙄 console output to it.


## Using konsole

In order to use konsole, you need to go through the usual motions of installing

```shell
(venv) project % python3 -m pip install konsole
```

and then importing the package

```python
import konsole
```

konsole automatically integrates itself with Python’s logging system the first
time the module is imported into an application. Notably, it registers a handler
that prints messages to standard error with the root logger, replaces the
current logger class with a subclass that supports the `detail` keyword
argument, and enables the capture of Python warnings through the logging system.

konsole's public API follows below. It consists of one function to update the
configuration, one function to access the `__main__` application logger, and six
functions to print messages at different priority levels. konsole includes type
annotations, which have been validated with
[mypy](https://mypy.readthedocs.io/en/stable/).


### Configuring konsole

  * Change the minimum level for printing messages and/or the flag for forcing
    colors on/off.

    ```python
    def config(
        *,
        level: Optional[int] = None,
        use_color: Optional[bool] = None,
        volume: Optional[int] = None,
    ) -> None: ...
    ```

    konsole starts out with `INFO` as minimum level and uses color if
    standard error is a TTY. The `volume` argument provides an alternative
    means for setting the output level, with larger volumes printing more
    information and 0 corresponding to the `W


### Logging Messages

  * Get the `__main__` application logger. konsole uses it for writing messages.

    ```python
    def logger() -> logging.Logger
    ```

    The logger, like any other logger created after the initialization of
    konsole, supports the `detail` keyword argument (see below).

  * Log a message at the given level.

    ```python
    def critical(msg: str, *args: object, **kwargs: object) -> None: ...
    def error(msg: str, *args: object, **kwargs: object) -> None: ...
    def warning(msg: str, *args: object, **kwargs: object) -> None: ...
    def info(msg: str, *args: object, **kwargs: object) -> None: ...
    def debug(msg: str, *args: object, **kwargs: object) -> None: ...
    def log(level: int, msg: str, *args: object, **kwargs: object) -> None: ...
    ```

    The message string is the first and only mandatory argument. If the message
    string contains `%` format specifiers, the necessary values must follow as
    positional arguments.

    Valid keyword arguments include those supported by Python's logging
    framework, notably `exc_info` for including an exception's stacktrace. They
    also include `detail` for supplemental data. konsole prints the mapping,
    sequence, or scalar value on separate, indented lines after the message but
    before an exception's stacktrace.

    konsole defines ALL CAPS constants, e.g., `WARNING`, for the five levels
    above. They have the same values as the corresponding constants in Python's
    logging package.


---

© 2022 [Robert Grimm](https://apparebit.com).
Subject to [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) license.
On [GitHub](https://github.com/apparebit/konsole).
On [PyPI](https://pypi.org/project/konsole/).
