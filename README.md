# konsole: readable, pleasing console output

> When you are writing a Python command line tool and your head is on fire
> because of overly rich frameworks that just don’t click.

[konsole](https://github.com/apparebit/konsole) is a simple logger built on top
of Python's `logging` framework that prints to standard error and, if the
underlying terminal is amenable, does so with the judicious use of bold and
light type as well as a dash of color. This package's interface stands on its
own, no experience or direct interaction with `logging` required. At the same
time, this package plays equally well with other loggers, just leave ~~konsole~~
🙄 console output to it.


## Using konsole

As usual, you first need to install konsole, preferably into a virtual
environment:

```shell
(venv) project % python3 -m pip install konsole
```

Once installed, add a call to `konsole.init()` at the very beginning of your
application's main function. The `init()` function, just like the rest of
konsole's public API, is described below. Both documentation and code include
type annotations, which have been validated with
[mypy](https://mypy.readthedocs.io/en/stable/).


### Configuring konsole

  * Initialize konsole with the given minimum level for printing messages and
    flag for forcing colors on or off. The default of `None` for the latter
    makes color dependent on whether standard error is a TTY.

    ```python
    def init(*, level: int = INFO, use_color: Optional[bool] = None) -> None: ...
    ```

    An application should call `init()` as soon as possible during startup. If
    it doesn't, konsole implicitly executes this function the first time any
    other function is invoked.

  * Force color on or off.

    ```python
    def set_color(use_color: bool) -> None: ...
    ```

  * Set the minimum level for printing messages.

    ```python
    def set_level(level: int) -> None: ...
    ```


### Logging Messages

  * Get the `__main__` application logger. konsole uses it for writing messages.

    ```python
    def logger() -> logging.Logger
    ```

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


### Redirecting Output

In theory, the `redirect_stderr` function in Python's `contextlib` would suffice
for redirecting the output of any Python class or module that writes to standard
error. In practice, that function is next to useless, since it naively assumes
that the class or module in question accesses standard error as `sys.stderr` on
each and every use. Hence:

  * Redirect konsole's output to the given stream. Unlike `redirect_stderr`,
    this function works.

    ```python
    def redirect(stream: TextIO) -> ContextManager[TextIO]: ...
    ```


---

© 2022 [Robert Grimm](https://apparebit.com). Code released under [Apache
2.0](https://www.apache.org/licenses/LICENSE-2.0) license.
