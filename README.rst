##########################
The ``native-lua`` Project
##########################

|appveyor-badge|_ |travis-badge|_ |cirrus-badge|_ |azure-badge|_ |readthedocs-badge|_ |license-badge|_



`Lua` is multi-paradigm programming language. `Lua` is cross-platform as it is
written in ANSI C. Lua is licensed under `MIT`_ license.

For information on `Lua` see `Lua.org`_.

********
Overview
********

As default `Lua` requires `gcc` and `make` to be installed to build the `Lua`
binaries, therefore building for e.g., Linux or other POSIX systems where `gcc`
and `make` are natively available is easy. Building `Lua` on Windows with
MinGWs' `gcc` and some sort of `make` is also straight forward.

But this does not allow a good platform and compiler independent way of building
and testing `Lua`, especially testing is not that simple as it should be.
Therefore this project tries a platform and compiler independent waf of building
**and** testing `Lua`.

******
How-To
******

Building `Lua` requires python 2.7 or greater and some C compiler.

.. code-block:: sh

  git clone https://github.com/swaldhoer/native-lua
  cd native-lua
  python waf configure

The output will show a number of successfully configured compilers, e.g., for
Windows with installed MSVC, gcc and clang the output should like this:

.. code-block:: sh

  ...
  Configured compilers                          : msvc, gcc, clang
  'configure' finished successfully

Now the build commands ``build_msvc``, ``build_gcc`` and ``build_clang`` should
work. The command concatenate is the same on all platforms, ``build_`` and then
the name of the successfully configured compiler.

.. code-block:: sh

  python waf build_gcc
  ...
  python waf install_gcc

For all build and test options on the platform see the output of

.. code-block:: sh

    python waf --help

*********************************
Supported Platforms And Compilers
*********************************

The current release supports the following platform/compiler combinations (*
means under development and/or untested):

+----------+-----------------------+---------------------+
| Platform | Official Lua Releases | Native Lua Releases |
+==========+=======================+=====================+
| aix      | - gcc                 | - xlc *             |
|          |                       | - gcc *             |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| bsd      | - gcc                 | - gcc *             |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| c89      | - gcc                 | all compilers *     |
+----------+-----------------------+---------------------+
| FreeBSD  | - gcc                 | - gcc *             |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| generic  | - gcc                 | - gcc (not win32)   |
|          |                       | - msvc (win32)      |
+----------+-----------------------+---------------------+
| linux    | - gcc                 | - gcc               |
|          |                       | - clang             |
|          |                       | - icc *             |
+----------+-----------------------+---------------------+
| macOS    | - gcc                 | - gcc *             |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| MinGW    | - gcc                 | see win32           |
+----------+-----------------------+---------------------+
| posix    | - gcc                 | - TODO              |
+----------+-----------------------+---------------------+
| solaris  | - gcc                 | - gcc *             |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| win32    | see MinGw             | - msvc              |
|          |                       | - gcc               |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| cygwin   | no                    | - gcc*              |
+----------+-----------------------+---------------------+

******************************************
Repository Structure And Code Organization
******************************************

Root Directory
==============

The root directory contains the

- general project documentation and a changelog (``README.rst``,
  ``CHANGELOG.rst``)
- build script (``wscript``),
- CI scripts (``.appveyor.yml``, ``.cirrus.yml``, ``.travis.yml``,
  ``azure-pipelines.yml``),
- editor configurations (``.vscode``, ``.editorconfig``),
- coding and general guidelines (``.flake8``, ``.pylintrc``,
  ``CONTRIBUTING.rst``),
- licensing information (``LICENSE``, ``CONTRIBUTING.rst``),
- and information on the lua version (``LUA_VERSION``).

``dl`` Directory
================

All files in the `dl` directory are the source and test files as they are
downloaded and extracted from `Lua.org`_ (for exceptions see the included
``README`` file).

The source and test files are tried to be kept in sync with the lua project
official website as fast as possible.

.. note::

    It is still possible to use the ``make`` based build, install etc. of the
    official Lua releases. Just ``cd`` into the ``dl/lua-5.3.4`` directory
    and everything should work.

``docs`` Directory
==================

Project documentation. The documentation from the official `Lua` releases is
currently **not** included outside the ``dl`` directory. The man files
(``lua.1``, ``luac.1``) however are included in ``docs/man`` and ``docs/man1``.

``src`` Directory
=================

This directory contains the source files coped from the ``dl`` directory.

All files are kept as they are downloaded from `Lua.org`_, except that trailing
whitespace and additional newlines at the end are removed.

``tests`` Directory
===================

This directory contains the test files coped from the ``dl`` directory.

All files are tried to be kept as they are downloaded from `Lua.org`_, except
that trailing whitespace and additional newlines at the end are removed as for
the sources. Furthermore for some tests, require changes to the test files in
order to work on Windows. The changes made to these files are indicated by the
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
- AppVeyor: Linux and Windows
- Cirrus CI: Linux and FreeBSD
- Travis CI: Linux, MacOS
- ReadTheDocs.org: Documentation

On AppVeyor we also run ``flake8`` and ``pylint``.

----

.. _lua.org: https://www.lua.org/
.. _MIT: https://www.lua.org/manual/5.3/readme.html#license
.. _lua_readme: https://www.lua.org/manual/5.3/readme.html

.. _readthedocs.io: https://native-lua.readthedocs.io/en/latest/

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
