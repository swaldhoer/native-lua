# The Why & The Goal Of This Project

[![Build status](https://ci.appveyor.com/api/projects/status/1gtcdi6wslxx3d6u/branch/master?svg=true)](https://ci.appveyor.com/project/swaldhoer/native-lua/branch/master)
[![Build Status](https://travis-ci.org/swaldhoer/native-lua.svg?branch=master)](https://travis-ci.org/swaldhoer/native-lua)
[![Build Status](https://api.cirrus-ci.com/github/swaldhoer/native-lua.svg)](https://cirrus-ci.com/github/swaldhoer/native-lua)
[![Documentation Status](https://readthedocs.org/projects/native-lua/badge/?version=latest)](https://native-lua.readthedocs.io/en/latest/?badge=latest)

`Lua` is multi-paradigm programming language. `Lua` is cross-platform as it is
written in ANSI C. Lua is licensed under [MIT license][1].
For information on `Lua` see [Lua.org][2]

## Overview

As default `Lua` requires `gcc` and `make` to be installed to build the `Lua`
binaries, therefore building for e.g., Linux or other POSIX systems where `gcc`
and `make` are natively available is easy, see [here][3]. Building `Lua` on
Windows with MinGWs' `gcc` and some sort of `make` is also straight forward.

But this does not allow a good platform and compiler independent way of building
and testing `Lua`, especially testing is not that simple as it should be.
Therefore this project tries a platform and compiler independent waf of building
**and** testing `Lua`.

## How-To

```bash
git clone https://github.com/swaldhoer/native-lua
cd native-lua
# to see possible options for your platform and compilers
python3 waf --help
python3 waf configure
# replace {compiler} accordingly to the successful configured compilers
python3 waf build_{compiler}
python3 waf install_{compiler}
```

For all build and test options see the output of `python3 waf --help`.

## Supported Platforms And Compilers

The current setup supports the following platform/compiler combinations (`*`
means under development and/or untested):

| Platform | Official Lua Releases             | Native Lua Releases                                                       |
|----------|-----------------------------------|---------------------------------------------------------------------------|
| aix      | <ul><li>[x] gcc </li></ul>        | <ul><li>[x] xlc`*` </li> <li>[x] gcc`*` </li> <li>[x] clang`*` </li></ul> |
| bsd      | <ul><li>[x] gcc </li></ul>        | <ul><li>[x] gcc`*` </li><li>[x] clang`*` </li></ul>                       |
| c89      | <ul><li>[x] gcc </li></ul>        | all compilers`*`                                                          |
| freebsd  | <ul><li>[x] gcc </li></ul>        | <ul><li>[x] gcc`*` </li><li>[x] clang`*` </li></ul>                       |
| generic  | <ul><li>[x] gcc </li></ul>        | TODO                                                                      |
| linux    | <ul><li>[x] gcc </li></ul>        | <ul><li>[x] gcc </li><li>[x] clang </li><li>[x] icc`*` </li></ul>         |
| macos    | <ul><li>[x] gcc </li></ul>        | <ul><li>[x] gcc`*` </li><li>[x] clang`*` </li></ul>                       |
| mingw    | <ul><li>[x] gcc </li></ul>        | see win32                                                                 |
| posix    | <ul><li>[x] gcc </li></ul>        | TODO                                                                      |
| solaris  | <ul><li>[x] gcc </li></ul>        | <ul><li>[x] gcc`*` </li><li>[x] clang`*` </li></ul>                       |
| win32    | see mingw                         | <ul><li>[x] msvc </li><li>[x] gcc </li><li>[x] clang`*` </li></ul>        |
| cygwin   | no                                | <ul><li>[x] gcc`*` </li></ul>                                             |

## Contents Of This Repository

### Content Directly Taken From The Lua Project

The following files are taken from the `Lua project`:

- all files in the `lua` directory, (except the ones ending with `_win.lua`)

  - subdirectory `lua-x.x.x` includes the sources to the specific version as
    downloaded from [Lua.org][2]

  - subdirectory `lua-x.x.x-tests` includes the tests to the specific version
    of lua as downloaded from [Lua.org][2]

The versions of sources and tests are tried to be kept in sync with the lua
project official website as fast as possible.

### Added Files By This Project

All other files in this repository are added by the `native-lua`-project,
except the following:

- `lua-x.x.x-tests/all_win.lua`: Basically the same file as `all.lua` from
  `lua-x.x.x-tests`, but as some tests do not work on windows, `all_win.lua`
  calls a test file with the suffix `_win.lua`, e.g., `main.lua` becomes
  `main_win.lua`. The changes made to the original file are indicated by
  `-- Added by 'native-lua' project,
  see https://github.com/swaldhoer/native-lua`.
- `lua-x.x.x-tests/main_win.lua`: Made test script work in `cmd`. The changes
  made to the original file are indicated by `-- Changed to cmd`.

## Links

The documentation can be found on
[readthedocs](https://native-lua.readthedocs.io/en/latest/).

---

[1]: https://www.lua.org/manual/5.3/readme.html#license
[2]: https://www.lua.org/
[3]: https://www.lua.org/manual/5.3/readme.html
