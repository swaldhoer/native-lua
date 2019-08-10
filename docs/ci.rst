##
CI
##

To test the project the continuous integration tools

- `AppVeyor`,
- `Azure Pipelines`,
- `Cirrus CI` and
- `Travis CI`.

are used.

**************
Project Status
**************

+--------------------+-----------------------+-------------------+
| CI Service         | Build Status          | Platform/compiler |
+====================+=======================+===================+
| AppVeyor           | |AppVeyorBUILD|       | - Windows         |
|                    |                       |                   |
|                    |                       |   - msvc          |
|                    |                       |   - gcc           |
|                    |                       |   - clang         |
|                    |                       |                   |
|                    |                       | - Ubuntu          |
|                    |                       |                   |
|                    |                       |   - gcc           |
|                    |                       |   - clang         |
+--------------------+-----------------------+-------------------+
| Azure Pipelines    | |AzurePipelinesBUILD| | - Windows         |
|                    |                       |                   |
|                    |                       |   - msvc (TODO)   |
|                    |                       |   - gcc (TODO)    |
|                    |                       |   - clang (TODO)  |
|                    |                       |                   |
|                    |                       | - Ubuntu          |
|                    |                       |                   |
|                    |                       |   - gcc           |
|                    |                       |   - clang         |
|                    |                       | - macOS           |
|                    |                       |                   |
|                    |                       |   - gcc (TODO)    |
|                    |                       |   - clang         |
+--------------------+-----------------------+-------------------+
| Travis-CI          | |TravisBUILD|         | - Ubuntu          |
|                    |                       |                   |
|                    |                       |   - gcc           |
|                    |                       |   - clang         |
|                    |                       |                   |
|                    |                       | - macOS           |
|                    |                       |                   |
|                    |                       |   - gcc (TODO)    |
|                    |                       |   - clang         |
+--------------------+-----------------------+-------------------+
| Cirrus-CI          | |CirrusBUILD|         | - Linux           |
|                    |                       |                   |
|                    |                       |   - gcc           |
|                    |                       |   - clang         |
|                    |                       |                   |
|                    |                       | - FreeBSD         |
|                    |                       |                   |
|                    |                       |   - gcc           |
|                    |                       |   - clang         |
+--------------------+-----------------------+-------------------+

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
