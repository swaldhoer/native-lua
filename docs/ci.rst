##
CI
##

To test the project binaries etc. the continuous integration tool `Travis CI <https://travis-ci.org/>`_
is used for Linux builds, and `AppVeyor <https://www.appveyor.com/>`_ is used for Windows builds.

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
