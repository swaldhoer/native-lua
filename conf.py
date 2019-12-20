#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=invalid-name

import os
import subprocess

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.graphviz",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
]

templates_path = [os.path.join("docs", "_templates")]

html_static_path = [os.path.join("docs", "_static")]

ON_RTD = os.environ.get("READTHEDOCS", None) == "True"
if ON_RTD:
    os.makedirs("_build/html/_doxygen", exist_ok=True)
    subprocess.call(
        '( cat doxygen.conf ; echo "OUTPUT_DIRECTORY=_build/html/_doxygen" ) | doxygen -',
        shell=True,
    )
else:
    html_static_path.append(os.path.join("docs", "_doxygen"))

source_suffix = ".rst"

master_doc = "index"

project = "native Lua"
copyright = "2018-2019, Stefan Waldhör"  # pylint: disable=redefined-builtin
author = "Stefan Waldhör"

version = "0.2.1"
release = version

language = "en"

exclude_patterns = []

pygments_style = "sphinx"

todo_include_todos = False

html_theme = "sphinx_rtd_theme"
html_theme_path = ["docs/_themes"]
html_theme_options = {}

htmlhelp_basename = "{}doc".format(project)
