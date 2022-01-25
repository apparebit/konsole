# konsole: readable, pleasing console output

`konsole` is a simple logger built on top of Python's `logging` framework that
prints to standard error and, if the underlying terminal is amenable, does so
with the judicious use of bold and light type as well as a dash of color. This
package's interface stands on its own, no experience or direct interaction with
`logging` required. At the same time, this package plays equally well with other
loggers, just leave ~~konsole~~ 🙄 console output to it.

To use konsole, your application should invoke the `init()` function as soon as
possible during startup, preferably before executing other application code. If
it instead invokes any of the other functions in konsole's public API —
`set_color()`, `set_level()`, `logger()`, `critical()`, `error()`, `warning()`,
`info()`, `debug()`, or `redirect()` — konsole implicitly invokes `init()` to
ensure proper initialization of its logging handler and formatter. Keep in mind
that delaying konsole's initialization that way also increases the likelihood of
some component writing to the log without the benefits of konsole's formatting.

---

© 2022 [Robert Grimm](https://apparebit.com). Code released under [Apache
2.0](https://www.apache.org/licenses/LICENSE-2.0) license.
