##############
Installing Lua
##############

After a successfully building with e.g. `gcc`, you can install lua by running:

.. code-block:: sh

   python waf install_gcc

On Unix-like systems the following files are installed:

- /usr/local/bin/

  - lua
  - luac

- /usr/local/include/

  - lua.h
  - luaconf.h
  - lualib.h
  - lauxlib.h
  - lua.hpp

- /usr/local/share/man/man1/

  - lua.1
  - luac.1

On Windows:

TODO
