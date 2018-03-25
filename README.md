[![Build status](https://ci.appveyor.com/api/projects/status/1gtcdi6wslxx3d6u/branch/master?svg=true)](https://ci.appveyor.com/project/swaldhoer/native-lua/branch/master)
[![Build Status](https://travis-ci.org/swaldhoer/dotnetcore-test.svg?branch=master)](https://travis-ci.org/swaldhoer/dotnetcore-test)

# The Why & The Goal Of This Project

Lua is  multi-paradigm programming language. Lua is cross-platform as it is
written in ANSI C. Lua is licensed under MIT license
(https://www.lua.org/manual/5.3/readme.html#license).
For information on `Lua` see [Lua.org](https://www.lua.org/)

Lua requires `make` to be installed to build the binaries,
therefore building for e.g., Linux or other POSIX systems where `make` is
natively available is easy, see
[here](https://www.lua.org/manual/5.3/readme.html).

Building Lua for Windows under Windows with native tools is nice
for Windows users and developers, but `make` is not available. Therefore this
project provides a `msbuild` project for building the binaries.



## Contents Of This Repository

### Content Directly Taken From The Lua Project

The following files are taken from the `Lua project` (modification in
**bold**):

- all files in the `lua` directory

  - subdirectory `lua-x.x.x` includes the sources to the specific version as
    downloaded from [Lua.org](https://www.lua.org/)

  - subdirectory `lua-x.x.x-tests` includes the tests to the specific version
    of lua as downloaded from [Lua.org](https://www.lua.org/).

The versions of sources and tests are tried to be kept in sync with the lua
project official website as fast as possible.

### Added Files By This Project

- All other files in this repository are added by the `native-lua`-project.
