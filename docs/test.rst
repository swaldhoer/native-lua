.. _TESTING_LUA:

###########
Testing Lua
###########

Testing the build involves the following steps:

- project configuration
- build lua/luac with some compiler
- installing lua and its dependencies
- running the tests

A script (``scripts/run_test.py``) is provided under to make this step more
convenient.
This script runs the full tests (that means **without** specifying
``-e"_U=true"``), but **without** using ``ltests``.
These parameters can however be set using command line arguments.
