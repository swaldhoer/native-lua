.. _CI:

##
CI
##

To test the project binaries etc. the continuous integration tool `Travis CI <https://travis-ci.org/>`_
is used for Linux builds, and `AppVeyor <https://www.appveyor.com/>`_ is used for Windows builds.

+---------+------------------+
| **OS**  | **Build Status** |
+=========+==================+
| Windows | |WINBUILD|       |
+---------+------------------+
| Linux   | |LINUXBUILD|     |
+---------+------------------+


.. |WINBUILD| image:: https://ci.appveyor.com/api/projects/status/1gtcdi6wslxx3d6u/branch/master?svg=true
  :target: https://ci.appveyor.com/project/swaldhoer/native-lua/branch/master
  :alt: Appveyor build status

.. |LINUXBUILD| image:: https://travis-ci.org/swaldhoer/native-lua.svg?branch=master
  :target: https://travis-ci.org/swaldhoer/native-lua
  :alt: Travis CI build status

*****************
Travis CI / Linux
*****************

Travis CI is configured by the `.travis.yml` file.

.. literalinclude:: ./../.travis.yml
   :caption: Travis CI configuration
   :language: yaml

******************
AppVeyor / Windows
******************
AppVeyor CI is configured by the `.appveyor.yml` file.

.. literalinclude:: ./../.appveyor.yml
   :caption: AppVeyor CI configuration
   :language: yaml
