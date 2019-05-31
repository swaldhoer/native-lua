##########################
The ``native-lua`` Project
##########################

|appveyor-badge|_ |travis-badge|_ |cirrus-badge|_ |readthedocs-badge|_



`Lua` is multi-paradigm programming language. `Lua` is cross-platform as it is
written in ANSI C. Lua is licensed under `MIT`_ license.
For information on `Lua` see `Lua.org`_.

********
Overview
********

As default `Lua` requires `gcc` and `make` to be installed to build the `Lua`
binaries, therefore building for e.g., Linux or other POSIX systems where `gcc`
and `make` are natively available is easy, see [here][3]. Building `Lua` on
Windows with MinGWs' `gcc` and some sort of `make` is also straight forward.

But this does not allow a good platform and compiler independent way of building
and testing `Lua`, especially testing is not that simple as it should be.
Therefore this project tries a platform and compiler independent waf of building
**and** testing `Lua`.

******
How-To
******

.. code-block::

  git clone https://github.com/swaldhoer/native-lua
  cd native-lua
  python waf configure
  # replace {compiler} accordingly to the successful configured compilers
  python waf build_{compiler}
  python waf install_{compiler}

For all build and test options see the output of

.. code-block::

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
|          |                       | - [ ] clang *       |
+----------+-----------------------+---------------------+
| bsd      | - gcc                 | - gcc *             |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| c89      | - gcc                 | all compilers *     |
+----------+-----------------------+---------------------+
| freebsd  | - gcc                 | - gcc *             |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| generic  | - gcc                 | - TODO              |
+----------+-----------------------+---------------------+
| linux    | - gcc                 | - gcc               |
|          |                       | - clang             |
|          |                       | - icc *             |
+----------+-----------------------+---------------------+
| macos    | - gcc                 | - gcc *             |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| mingw    | - gcc                 | see win32           |
+----------+-----------------------+---------------------+
| posix    | - gcc                 | - TODO              |
+----------+-----------------------+---------------------+
| solaris  | - gcc                 | - gcc *             |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| win32    | see mingw             | - msvc              |
|          |                       | - gcc               |
|          |                       | - clang *           |
+----------+-----------------------+---------------------+
| cygwin   | no                    | - gcc*              |
+----------+-----------------------+---------------------+

***************************
Contents Of This Repository
***************************

Content Directly Taken From The Lua Project
===========================================

All files in the `lua` directory, (except the ones ending with ``_win.lua``) are
from `Lua.org`_. All files are as they are downloaded from `Lua.org`_, except
that trailing whitespace and additional newlines at the end of file have been
removed. In ``lua/tests/libs/`` the ``Makefile`` needed to be adapted to work
with this repository structure.

.. note::

    It is still possible to use the ``make`` based build, install etc. of the
    official Lua releases. Just ``cd`` into the lua directory  and everything
    should work fine.

The source is tried to be kept in sync with the lua project official website as
fast as possible.

The current version of `Lua` is described in the file ``LUA_VERSION``.

Added Files By The ``native-lua`` Project
=========================================

All other files in this repository are added by the `native-lua`-project,
except the following.

For the tests, some of the test files needed to be adapted to work on Windows.
The changes made to these files are indicated by

.. code-block::

    -- Added by 'native-lua' project, see https://github.com/swaldhoer/native-lua.

*****
Links
*****

The documentation can be found on `readthedocs.io`_.

**
CI
**

- AppVeyor: Linux and Windows
- Cirrus CI: Linux and FreeBSD
- Travis CI: Linux
- ReadTheDocs.org

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

.. |readthedocs-badge| image:: https://readthedocs.org/projects/native-lua/badge/?version=latest
.. _readthedocs-badge: https://native-lua.readthedocs.io/en/latest/?badge=latest
