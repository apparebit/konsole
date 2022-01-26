# konsole changelog

### v0.2.0 (xx Jan 2022):

  * Surface `detail` keyword argument for logging functions.
  * Document konsole's public API.
  * Correctly handle corner cases of `detail` being `None`,
    `set_color()` and `set_level()` calling `init()`.
  * Cache main logger and directly access flag to eliminate repeated, trivial
    function calls.

### v0.1.0: 25 Jan 2022

Initial release.
