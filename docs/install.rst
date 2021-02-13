##############
Installing Lua
##############

After a successfully building lua binaries with e.g. `gcc`, you can install lua
by running:

.. platform-picker::

    .. platform-choice:: windows
        :title: Windows

        .. code-block:: batch

           waf install_gcc

    .. platform-choice:: linux
        :title: Linux/Unix/Unix-like/macOS

        .. code-block:: bash

           $ python3 waf install_gcc

The following files are installed:

.. platform-picker::

    .. platform-choice:: windows
        :title: Windows

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

    .. platform-choice:: linux
        :title: Linux/Unix/Unix-like/macOS

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
