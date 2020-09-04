######################
Continuous Integration
######################

To test the project the continuous integration tools

- `AppVeyor`,
- `Azure Pipelines`,
- `Cirrus CI` and
- `Travis CI`.

are used.

**************
Project Status
**************

+--------------------+-----------------------+--------------------------------------------------------------+
| CI Service         | Build Status          | Platform on Architecture with compiler                       |
+====================+=======================+==============================================================+
| AppVeyor           | |AppVeyorBUILD|       | - Windows (Server 2019) on AMD64                             |
|                    |                       |                                                              |
|                    |                       |   - Cygwin                                                   |
|                    |                       |                                                              |
|                    |                       |     - gcc                                                    |
|                    |                       |     - clang                                                  |
+--------------------+-----------------------+--------------------------------------------------------------+
| Azure Pipelines    | |AzurePipelinesBUILD| | - Windows (Server 2019) on AMD64                             |
|                    |                       |                                                              |
|                    |                       |   - msvc (2019)                                              |
|                    |                       |   - gcc (8.1.0)                                              |
|                    |                       |   - clang (10.0.0)                                           |
|                    |                       |                                                              |
|                    |                       | - Linux (Ubuntu 18.04) on AMD64                              |
|                    |                       |                                                              |
|                    |                       |   - gcc (7.4.0)                                              |
|                    |                       |   - clang (10.0.0)                                           |
|                    |                       |                                                              |
|                    |                       | - Unix (macOS 10.14) on AMD64                                |
|                    |                       |                                                              |
|                    |                       |   - gcc (9.2.0)                                              |
|                    |                       |   - clang (11.0.0)                                           |
+--------------------+-----------------------+--------------------------------------------------------------+
| Travis-CI          | |TravisBUILD|         | - Linux (Ubuntu 16.04, Ubuntu 18.04) on AMD64, S390x, ARM64  |
|                    |                       |                                                              |
|                    |                       |   - gcc (5.4.0, 7.4.0)                                       |
|                    |                       |   - clang (7.0.0, 7.0.0)                                     |
+--------------------+-----------------------+--------------------------------------------------------------+
| Cirrus-CI          | |CirrusBUILD|         | - Linux (Ubuntu 18.04, Fedora 30, Debian 10) on AMD64        |
|                    |                       |                                                              |
|                    |                       |   - gcc (7.4.0, 9.2.1, 10.x.x)                               |
|                    |                       |   - clang (9.0.1, 8.0.0, 9.0.1)                              |
|                    |                       |                                                              |
|                    |                       | - Unix (FreeBSD 12.1) on AMD64                               |
|                    |                       |                                                              |
|                    |                       |   - gcc (9.2.0)                                              |
|                    |                       |   - clang (8.0.1)                                            |
+--------------------+-----------------------+--------------------------------------------------------------+

*********************
Configuration Details
*********************

AppVeyor
========

AppVeyor CI is configured by the ``.appveyor.yml`` file.

.. literalinclude:: ./../.appveyor.yml
   :caption: AppVeyor CI configuration
   :language: yaml

Azure Pipelines
===============

Azure Pipelines CI is configured by the ``azure-pipelines.yml`` file.

.. literalinclude:: ./../azure-pipelines.yml
   :caption: Azure Pipelines CI configuration
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

.. |AzurePipelinesBUILD| image:: https://dev.azure.com/stefanwaldhoer/stefanwaldhoer/_apis/build/status/swaldhoer.native-lua?branchName=master
   :target: https://dev.azure.com/stefanwaldhoer/stefanwaldhoer/
   :alt: Azure Pipelines build status

.. |TravisBUILD| image:: https://travis-ci.org/swaldhoer/native-lua.svg?branch=master
   :target: https://travis-ci.org/swaldhoer/native-lua
   :alt: Travis CI build status

.. |CirrusBUILD| image:: https://api.cirrus-ci.com/github/swaldhoer/native-lua.svg
   :target: https://cirrus-ci.com/github/swaldhoer/native-lua
   :alt: Cirrus CI build status
