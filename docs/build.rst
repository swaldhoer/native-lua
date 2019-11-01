############
Building Lua
############

********
Building
********

To build `Lua` on your platform, check which compilers were successfully
configured. If e.g., `gcc` was successfully configured, simply run:

.. code-block:: sh

   python waf build_gcc

*************************
General Build Information
*************************

native Lua tries to follow the official build instructions are far as possible.
This means:

- Build a statically linked library based on the following files:

  - ``lapi.c``
  - ``lcode.c``
  - ``ldo.c``
  - ``lctype.c``
  - ``ldebug.c``
  - ``ldump.c``
  - ``lfunc.c``
  - ``lgc.c``
  - ``llex.c``
  - ``lmem.c``
  - ``lobject.c``
  - ``lopcodes.c``
  - ``lparser.c``
  - ``lstate.c``
  - ``lstring.c``
  - ``ltable.c``
  - ``ltm.c``
  - ``lundump.c``
  - ``lvm.c``
  - ``lzio.c``
  - ``lauxlib.c``
  - ``lbaselib.c``
  - ``lbitlib.c``
  - ``lcorolib.c``
  - ``ldblib.c``
  - ``liolib.c``
  - ``lmathlib.c``
  - ``loslib.c``
  - ``lstrlib.c``
  - ``ltablib.c``
  - ``lutf8lib.c``
  - ``loadlib.c``
  - ``linit.c``

- Windows only: Build a dynamically linked library based on the same files as
  the statically linked library.

- Build the interpreter (source: ``lua.c``) and link with the statically linked
  library (Unix-like) or with the dynamically linked library on Windows.

- Build the compiler (source: ``luac.c``) and link with the statically linked
  library.

*******************************************
Implementation Details Of The Build Process
*******************************************

``native Lua`` uses waf as build tool. For details on waf see
`waf.io <https://waf.io/>`. The build instructions are implement in the build
script ``wscript``.

The build process consists of two steps:

- configuration
- build

During the configure step platform and compiler specific settings are created.
A list of successfully configured compilers is created.

For details see the function ``configure`` in ``wscript``.

The build step is specific for most platforms. There are build functions for
each supported platform.

For details see the function ``build`` in ``wscript``.

***********************
OS Specific Information
***********************

TODO
