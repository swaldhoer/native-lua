#########
Changelog
#########

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ v1.0.0, and this project adheres to
`Semantic Versioning`_ v2.0.0.

************
[Unreleased]
************

********************
[0.1.0] - 2019-07-XX
********************

Added
=====

- Added a rules for contributing to the project (see ``CONTRIBUTING.md``).
- Added a script to make testing simpler (``scripts/run_test.py``)
- Added `generic` build option.
- Added ``LUA_VERSION`` file to indicate the lua version obtained from
  `lua.org`_.
- `include` and `man` files are installed.

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

- ``lua/wscript``, see section `Changed`

Fixed
=====

- Use correct include path of the of the `readline` library on FreeBSD when
  using clang.
- Use correct `rpath` on FreeBSD when using gcc.
- Fixed clang linker flag on OSX

Security
========

.. _Keep a Changelog : https://keepachangelog.com/en/1.0.0/

.. _Semantic Versioning : https://semver.org/spec/v2.0.0.html

.. _lua.org : https://www.lua.org/
