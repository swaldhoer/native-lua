# The Why & The Goal Of This Project

[![Build status](https://ci.appveyor.com/api/projects/status/1gtcdi6wslxx3d6u/branch/master?svg=true)](https://ci.appveyor.com/project/swaldhoer/native-lua/branch/master)
[![Build Status](https://travis-ci.org/swaldhoer/native-lua.svg?branch=master)](https://travis-ci.org/swaldhoer/native-lua)

Lua is  multi-paradigm programming language. Lua is cross-platform as it is
written in ANSI C. Lua is licensed under [MIT license][1].
For information on `Lua` see [Lua.org][2]

Lua requires `make` to be installed to build the binaries,
therefore building for e.g., Linux or other POSIX systems where `make` is
natively available is easy, see [here][3].

Building Lua for Windows under Windows with native tools (therefore not building
with `MinGW` or `Cygwin`) is nice for Windows users and developers, but `make`
is not available. Therefore this project provides a `msbuild` project for
building the binaries.

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
- `lua-x.x.x-tests/main_win.lua`: made test script work in `cmd`. The changes
  made to the original file are indicated by `-- Changed to cmd`.

## Links

### [Building Lua](doc/build.md)

### [Installing Lua](doc/install.md)

### [Testing Lua](doc/test.md)

### [CI](doc/ci.md)

[1]: https://www.lua.org/manual/5.3/readme.html#license
[2]: https://www.lua.org/
[3]: https://www.lua.org/manual/5.3/readme.html
