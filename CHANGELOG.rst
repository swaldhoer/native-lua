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

Changed
=======

- Pasted `build` step from ``lua/wscript`` to ``wscript`` to have only one
  ``wscript``. These changes should be transparent.
- Rewrote `configure` step to print better readable output.
- Restructured the way sources, documentation etc. are stored.

Deprecated
==========

Removed
=======

- ``lua/wscript``, see section `Changed`.
- Removed support for python versions < 3.5

Fixed
=====

- Use correct include path of the of the `readline` library on FreeBSD when
  using clang.
- Use correct `rpath` on FreeBSD when using gcc.
- Fixed clang linker flag on OSX.
- Fixed clang linker flags on Windows.
- Fix name (``LICENSE``)

Security
========

.. _Keep a Changelog : https://keepachangelog.com/en/1.0.0/

.. _Semantic Versioning : https://semver.org/spec/v2.0.0.html

.. _lua.org : https://www.lua.org/
