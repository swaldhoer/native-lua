##
CI
##

To test the project the continuous integration tools

- `AppVeyor <https://www.appveyor.com/>`_,
- `Cirrus CI <https://www.appveyor.com/>`_ and
- `Travis CI <https://travis-ci.org/>`_

are used.

**************
Project Status
**************

+-------------+-------------------+-------------------+
| CI Service  | Build Status      | Platform/compiler |
+=============+===================+===================+
| AppVeyor    | |AppVeyorBUILD|   | - Windows         |
|             |                   |                   |
|             |                   |   - MSVC          |
|             |                   |   - gcc           |
|             |                   |   - clang         |
|             |                   |                   |
|             |                   | - Ubuntu          |
|             |                   |                   |
|             |                   |   - gcc           |
|             |                   |   - clang         |
+-------------+-------------------+-------------------+
| Travis-CI   | |TravisBUILD|     | - Ubuntu          |
|             |                   |                   |
|             |                   |   - gcc           |
|             |                   |   - clang         |
+-------------+-------------------+-------------------+
| Cirrus-CI   | |CirrusBUILD|     | - Linux           |
|             |                   |                   |
|             |                   |   - gcc           |
|             |                   |   - clang         |
|             |                   |                   |
|             |                   | - FreeBSD         |
|             |                   |                   |
|             |                   |   - gcc           |
|             |                   |   - clang         |
+-------------+-------------------+-------------------+

*********************
Configuration Details
*********************

AppVeyor
========

AppVeyor CI is configured by the ``.appveyor.yml`` file.

.. literalinclude:: ./../.appveyor.yml
   :caption: AppVeyor CI configuration
   :language: yaml

Cirrus CI
=========

Cirrus CI is configured by the ``.cirrus.yml`` file.

.. literalinclude:: ./../.cirrus.yml
   :caption: Cirrus CI configuration
   :language: yaml

Travis CI
=========

Travis CI is configured by the ``.travis.yml`` file.

.. literalinclude:: ./../.travis.yml
   :caption: Travis CI configuration
   :language: yaml

.. |AppVeyorBUILD| image:: https://ci.appveyor.com/api/projects/status/1gtcdi6wslxx3d6u/branch/master?svg=true
  :target: https://ci.appveyor.com/project/swaldhoer/native-lua/branch/master
  :alt: Appveyor build status

.. |TravisBUILD| image:: https://travis-ci.org/swaldhoer/native-lua.svg?branch=master
  :target: https://travis-ci.org/swaldhoer/native-lua
  :alt: Travis CI build status

.. |CirrusBUILD| image:: https://api.cirrus-ci.com/github/swaldhoer/native-lua.svg
  :target: https://cirrus-ci.com/github/swaldhoer/native-lua
  :alt: Cirrus CI build status
