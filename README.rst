##########################
The ``native Lua`` Project
##########################

|appveyor-badge|_ |travis-badge|_ |cirrus-badge|_ |azure-badge|_ |readthedocs-badge|_ |license-badge|_ |code-style-black-badge|_

**Lua on the platform you use with the compiler you chose**

`Lua` is multi-paradigm programming language. `Lua` is cross-platform as it is
written in ANSI C. Lua is licensed under `MIT`_ license. ``native Lua`` goal is
to deliver a framework to build `Lua` on any platform with any compiler:

For information on `Lua` see `Lua.org`_.

********
Overview
********

As default `Lua` requires `gcc` and `make` to be installed to build the `Lua`
binaries, therefore building for e.g., Linux or other POSIX systems where `gcc`
and `make` are natively available is easy. Building `Lua` on Windows with
MinGWs' `gcc` and some sort of `make` is also straight forward.

But this does not allow a good platform and compiler independent way of building
and testing `Lua`. Especially testing is not that simple as it should be.
Therefore this project tries to implement a platform and compiler independent
way of building **and** testing `Lua`.

******
How-To
******

Building `Lua` with the `native Lua` project requires python 2.7 or greater and
some C compiler.

.. image:: docs/_static/basic-cmds.gif
   :alt: alternate text

*********************************
Supported Platforms And Compilers
*********************************

The current release supports the following platform/compiler combinations:

+----------+-----------------------+-------------------------------+
| Platform | Official Lua Releases | ``native Lua`` Releases       |
+==========+=======================+===============================+
| aix      | gcc                   | xlc*, gcc*, clang*            |
+----------+-----------------------+-------------------------------+
| bsd      | gcc                   | gcc*, clang*                  |
+----------+-----------------------+-------------------------------+
| c89      | gcc                   | all compilers*                |
+----------+-----------------------+-------------------------------+
| FreeBSD  | gcc                   | gcc, clang                    |
+----------+-----------------------+-------------------------------+
| generic  | gcc                   | gcc (not win32), msvc (win32) |
+----------+-----------------------+-------------------------------+
| linux    | gcc                   | gcc, clang, icc*              |
+----------+-----------------------+-------------------------------+
| macOS    | gcc                   | gcc*, clang*                  |
+----------+-----------------------+-------------------------------+
| MinGW    | gcc                   | see win32                     |
+----------+-----------------------+-------------------------------+
| posix    | gcc                   | TODO                          |
+----------+-----------------------+-------------------------------+
| solaris  | gcc                   | gcc*, clang*                  |
+----------+-----------------------+-------------------------------+
| win32    | see MinGw             | msvc, gcc, clang              |
+----------+-----------------------+-------------------------------+
| cygwin   | no                    | gcc*                          |
+----------+-----------------------+-------------------------------+

\* means not or not fully tested.

******************************************
Repository Structure And Code Organization
******************************************

The repository is structured into the parts described below.

Root Directory
==============

The root directory contains the

- general project documentation and a changelog (``README.rst``,
  ``CHANGELOG.rst``)
- build script (``wscript``),
- CI scripts (``.appveyor.yml``, ``.cirrus.yml``, ``.travis.yml``,
  ``azure-pipelines.yml``),
- editor configurations (``.vscode``, ``.editorconfig``),
- coding and general guidelines (``pyproject.toml``, ``.pylintrc``,
  ``CONTRIBUTING.rst``),
- licensing information (``LICENSE``, ``CONTRIBUTING.rst``),
- and information on the lua version (``LUA_VERSION``).

``demos`` Directory
===================

Some scripts demonstrating what can be done with Lua. These demos should not
use libraries that do not come with the `Lua` interpreter.

``docs`` Directory
==================

This directory contains the `native Lua` project documentation as well as the
official `Lua` documentation. The official `Lua` documentation is found in
`docs/_static/doc`. This documentation is also linked into the project
documentation.

``src`` Directory
=================

This directory contains the source files as they are downloaded from `Lua.org`_,
except that trailing whitespace and additional newlines at the end of the files
are removed.

``tests`` Directory
===================

This directory contains the test files as they are downloaded from `Lua.org`_,
except that trailing whitespace and additional newlines at the end of the files
are removed.

Furthermore for some tests, require changes to the test files in order to work
on platforms. The changes made to these files are indicated by the
following line:

.. code-block:: sh

   -- Added by 'native-lua' project, see https://github.com/swaldhoer/native-lua.

*****
Links
*****

The documentation can be found on `readthedocs.io`_.

**
CI
**

- Azure Pipelines: Linux, MacOS
- AppVeyor: Linux, Windows
- Cirrus CI: Linux, FreeBSD
- Travis CI: Linux, MacOS
- ReadTheDocs.org: Documentation

On AppVeyor's Windows build we also run |black|_ and |pylint|_.

----

.. _lua.org: https://www.lua.org/
.. _MIT: https://www.lua.org/manual/5.3/readme.html#license
.. _lua_readme: https://www.lua.org/manual/5.3/readme.html

.. _readthedocs.io: https://native-lua.readthedocs.io/en/latest/

.. |black| replace:: ``black``
.. _black: https://black.readthedocs.io/en/stable/

.. |pylint| replace:: ``pylint``
.. _pylint: https://www.pylint.org/

.. |appveyor-badge| image:: https://ci.appveyor.com/api/projects/status/1gtcdi6wslxx3d6u/branch/master?svg=true
.. _appveyor-badge: https://ci.appveyor.com/project/swaldhoer/native-lua/branch/master

.. |travis-badge| image:: https://travis-ci.org/swaldhoer/native-lua.svg?branch=master
.. _travis-badge: https://travis-ci.org/swaldhoer/native-lua

.. |cirrus-badge| image:: https://api.cirrus-ci.com/github/swaldhoer/native-lua.svg
.. _cirrus-badge: https://cirrus-ci.com/github/swaldhoer/native-lua

.. |azure-badge| image:: https://dev.azure.com/stefanwaldhoer/stefanwaldhoer/_apis/build/status/swaldhoer.native-lua?branchName=master
.. _azure-badge: https://dev.azure.com/stefanwaldhoer/stefanwaldhoer/

.. |readthedocs-badge| image:: https://readthedocs.org/projects/native-lua/badge/?version=latest
.. _readthedocs-badge: https://native-lua.readthedocs.io/en/latest/?badge=latest

.. |license-badge| image:: https://img.shields.io/github/license/swaldhoer/native-lua.svg
.. _license-badge: https://github.com/swaldhoer/native-lua/blob/master/LICENSE

.. |code-style-black-badge| image:: https://img.shields.io/badge/code%20style-black-000000.svg
.. _code-style-black-badge: https://github.com/python/black
