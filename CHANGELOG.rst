#########
Changelog
#########

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ v1.0.0, and this project adheres to
`Semantic Versioning`_ v2.0.0.

************
[Unreleased]
************

Added
=====

- Added doxygen configuration (see ``doxygen.conf``, ``docs/_doxygen/*``).
- Added support for **OpenBSD** and **NetBSD** (``wscript``).

Changed
=======

- Simplified the library build test (``wscript``).

Fixed
=====

- Build function for **Solaris** was wrong (``wscript``).

********************
[0.2.1] - 2019-12-01
********************

Changed
=======

- ``lua -v`` showed the wrong version information.

********************
[0.2.0] - 2019-11-23
********************

Added
=====

- Added header for C/C++ files (see ``CONTRIBUTING.rst``).
- Added the license information for sphinx_rtd_theme
  (``docs/_themes/sphinx_rtd_theme/LICENSE``).
- Added information on the build and install process (``docs/build.rst``,
  ``docs/install.rst``).

Changed
=======

- Updated to Lua version 5.3.5 (see ``src/*``).
- Updated `sphinx_rtd_theme` to 2a1b2e1353f6401af96885a66488ac0811110ba2.
- Check that all version numbers in the project match during project
  configuration (``wscript``).
- Use yaml to load the version information from ``VERSION`` file.
- Issue a warning if the lua binaries are installed into a directory that is
  not available in PATH.

Removed
=======

- Unused file ``tests/all_win.lua`` has been removed.

Fixed
=====

- Lua manual was not correctly linked into the documentation. Now man files are
  correctly installed into ``man/man1`` on Unix-like systems.
- Fixed list of tested compilers and platforms (``README.rst``).
- Consequently use the correct project name ``native Lua`` (previously
  ``native-lua``).
- man files were installed into $PREFIX. Now they are correctly installed into
  man/man1.
- Fixed linker flags on macOS when using GCC

********************
[0.1.0] - 2019-10-15
********************

Added
=====

- Added a rules for contributing to the project (see ``CONTRIBUTING.rst``).
- Added a script to make testing simpler (``scripts/run_test.py``).
- Added `generic` build option.
- Added ``VERSION`` file to indicate the native Lua project version and the lua
  and lua tests version obtained from `lua.org`_.
- `include` and `man` files are installed.
- added `sphinx_rtd_theme` (based on commit
  feb0beb44a444f875f3369a945e6055965ee993f from
  https://github.com/readthedocs/sphinx_rtd_theme)
- Added a batch wrapper script for waf on Windows (``waf.bat``)
- Added test files for Windows and Cygwin to test the build tools
- For Linux (clang, gcc), macOS (clang), FreeBSD (clang, gcc) and Windows
  (clang, gcc, msvc) the lua test suite passes with ``lua -e"_U=true" all.lua``

Changed
=======

- Pasted `build` step from ``lua/wscript`` to ``wscript`` to have only one
  ``wscript``. These changes should be transparent.
- Rewrote `configure` step to print better readable output.
- Restructured the way sources, documentation etc. are stored.

Removed
=======

- ``lua/wscript``, see section `Changed`.
- Removed support for Python versions < 3.5

Fixed
=====

- Use correct include path of the of the `readline` library on FreeBSD when
  using clang.
- Use correct `rpath` on FreeBSD when using gcc.
- Fixed clang linker flag on OSX.
- Fixed clang linker flags on Windows.
- Fix name (``LICENSE``)
- Fixed typos

.. _Keep a Changelog : https://keepachangelog.com/en/1.0.0/

.. _Semantic Versioning : https://semver.org/spec/v2.0.0.html

.. _lua.org : https://www.lua.org/
