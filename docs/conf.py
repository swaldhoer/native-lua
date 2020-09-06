#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=invalid-name

import os
import subprocess

import sphinx_rtd_theme  # pylint: disable=unused-import

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
    "sphinx_rtd_theme",
    "sphinx_copybutton",
]

nitpicky = True


def setup(app):
    app.add_css_file("custom.css")


templates_path = ["_templates"]

html_static_path = ["_static", "_doxygen"]

ON_RTD = os.environ.get("READTHEDOCS", None) == "True"
if ON_RTD:
    os.makedirs("_build/html/_doxygen", exist_ok=True)
    subprocess.call(
        '( cat doxygen.conf ; echo "OUTPUT_DIRECTORY=_build/html/_doxygen" ) | doxygen -',
        shell=True,
    )

source_suffix = ".rst"

master_doc = "index"

project = "native Lua"
copyright = "2018-2020, Stefan Waldhör"  # pylint: disable=redefined-builtin
author = "Stefan Waldhör"

version = "0.5.0-devel"
release = version

language = "en"

exclude_patterns = []

pygments_style = "sphinx"

todo_include_todos = False

html_theme = "sphinx_rtd_theme"
html_theme_options = {}

htmlhelp_basename = "{}doc".format(project)
