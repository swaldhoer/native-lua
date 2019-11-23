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

On Windows the following files are installed:

- %LOCALAPPDATA%\\Programs\\lua\\bin

  - lua.exe
  - lua.exe.manifest (msvc only)
  - luac.exe
  - luac.exe.manifest (msvc only)
  - luadll.dll
  - luadll.dll.manifest (msvc only)

- %LOCALAPPDATA%\\Programs\\lua\\include

  - lauxlib.h
  - lua.h
  - lua.hpp
  - luaconf.h
  - lualib.h

- %LOCALAPPDATA%\\Programs\\lua\\lib
  - luadll.dll.a (gcc only)
  - luadll.dll (clang, msvc only)
  - luadll.dll.manifest (msvc only)
  - luadll.lib (msvc only)
