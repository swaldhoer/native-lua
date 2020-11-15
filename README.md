# The ``native Lua`` Project

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/swaldhoer/native-lua)
[![Build status](https://ci.appveyor.com/api/projects/status/1gtcdi6wslxx3d6u?svg=true)](https://ci.appveyor.com/project/swaldhoer/native-lua)
[![Build Status](https://travis-ci.com/swaldhoer/native-lua.svg?branch=master)](https://travis-ci.com/swaldhoer/native-lua)
[![Build Status](https://api.cirrus-ci.com/github/swaldhoer/native-lua.svg)](https://cirrus-ci.com/github/swaldhoer/native-lua)
[![Build Status](https://dev.azure.com/stefanwaldhoer/native-lua/_apis/build/status/swaldhoer.native-lua?branchName=master)](https://dev.azure.com/stefanwaldhoer/native-lua/_build/latest?definitionId=1&branchName=master)
[![Documentation Status](https://readthedocs.org/projects/native-lua/badge/?version=latest)](https://native-lua.readthedocs.io/en/latest/?badge=latest)
![GitHub](https://img.shields.io/github/license/swaldhoer/native-lua)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

**native Lua** - Lua on the platform you use with the compiler you choose

[Lua](https://www.lua.org/) is multi-paradigm programming language. Lua is
cross-platform as it is written in ANSI C. Lua is licensed under
[MIT](https://www.lua.org/manual/5.4/readme.html#license) license. For more
information on Lua see [lua.org](https://www.lua.org).

`native Lua` delivers a framework to **build** and **test** Lua on **any**
platform with **any** compiler.

## Overview

By default Lua requires [gcc](https://gcc.gnu.org/) and
[make](https://www.gnu.org/software/make/) to be installed to build the
Lua binaries, therefore building for e.g., Linux or POSIX systems where gcc and
make are natively available is easy. Building Lua on Windows with MinGWs' gcc
and some sort of make is also straight forward.

But this does not allow a good platform and compiler independent way of
building and testing Lua. Especially testing is not that simple as it should
be. Therefore this project implements a platform and compiler independent way
of building and testing Lua.

## How-To

Building Lua with the `native Lua` project requires Python 3.5 or greater and
some C compiler. Exemplary Windows build using gcc:

1. ``waf.bat configure``
1. ``waf.bat build_gcc``
1. ``waf.bat install_gcc``

![Configure and build Lua on Windows using gcc](docs/_static/basic-cmds.gif)

## Supported Platforms And Compilers

The current release supports the following platform/compiler combinations:

| Platform | Official Lua Releases | `native Lua` Releases         |
| -------- | --------------------- | ----------------------------- |
| aix      | gcc                   | xlc*, gcc*, clang*            |
| bsd      | gcc                   | see OpenBSD and NetBSD        |
| OpenBSD  | see bsd               | gcc, clang                    |
| NetBSD   | see bsd               | gcc*, clang*                  |
| c89      | gcc                   | all compilers*                |
| FreeBSD  | gcc                   | gcc, clang                    |
| generic  | gcc                   | gcc (not win32), msvc (win32) |
| linux    | gcc                   | gcc, clang, icc*              |
| macOS    | gcc                   | gcc, clang                    |
| MinGW    | gcc                   | see win32                     |
| posix    | gcc                   | TODO                          |
| solaris  | gcc                   | gcc*, clang*                  |
| win32    | see MinGw             | msvc, gcc, clang              |
| cygwin   | no                    | gcc, clang                    |

\* means not or not fully tested.

## Repository Structure And Code Organization

The repository is structured into the parts described below.

### Root Directory

The root directory contains the

- general project documentation (``README.md``, ``CHANGELOG.md``)
- build script and build toolchain (``wscript``, ``waf``, ``waf.bat``),
- required Python packages (``requirements.txt``, ``environment.yml``),
- CI scripts (``.appveyor.yml``, ``.cirrus.yml``, ``.travis.yml``,
  ``azure-pipelines.yml``, ``readthedocs.yml``),
- editor configurations (``.vscode``, ``.editorconfig``),
- coding and general guidelines (``pyproject.toml``),
- licensing information (``LICENSE``),
- and information on the ``native Lua`` project and the lua version
  (``VERSION``).

### ``demos`` Directory

Some scripts demonstrating what can be done with Lua. These demos should not
use libraries that do not come with the Lua interpreter.

### ``docs`` Directory

This directory contains the `native Lua` project documentation as well as the
official Lua documentation. The official Lua documentation is found in
``_static/doc``. This documentation is also linked into the project
documentation. The main documentation files ``index.rst``, ``conf.py`` and
``doxygen.conf`` are found here. Contribution guidelines are found in
``contributing.rst``.

`native Lua` uses the
[ReadTheDocs Sphinx theme](https://github.com/readthedocs/sphinx_rtd_theme) as
layout theme for the documentation.

### ``src`` Directory

This directory contains the source files downloaded from
[lua.org/ftp](https://www.lua.org/ftp/#source). Trailing whitespace and
additional newlines at the end of the files are removed. Furthermore the native
Lua header is included
(see [_native_lua_config.h](src/_native_lua_config.h)).

Changes to original Lua sources are indicated by the following comment:

```c
/* native Lua */
```

The lua interpreter (``lua.c``) as well as the lua compiler (``luac.c``) have
been changed, to indicate, that they were build based on the `native Lua`
project:

```shell
$ build/gcc/lua -v
Lua 5.4.0  Copyright (C) 1994-2017 Lua.org, PUC-Rio [based on native Lua (0.5.0-devel), https://github.com/swaldhoer/native-lua]
```

### ``tests`` Directory

This directory contains the source files downloaded from
[lua.org/tests](https://www.lua.org/tests). Trailing whitespace and additional
newlines at the end of the files are removed.

> **Note:** The encoding of test files **must not** be changed.

Some tests require changes to the test files in order to work on platforms.

Changes to original Lua test sources are indicated by the following comment:

```lua
-- native Lua
```

Test files for the build toolchain have been added in ``tests/build``.

## Documentation

Built versions of the documentation are found on
[native-lua.readthedocs.io](https://native-lua.readthedocs.io/en/latest/).

## License

`native Lua` is licensed under the terms of the [MIT](LICENSE) license.
