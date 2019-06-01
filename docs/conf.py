#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import sphinx_rtd_theme

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.graphviz',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    ]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = 'native-lua'
copyright = '2018-2019, Stefan Waldhoer'
author = 'Stefan Waldhoer'

version = '0.0.1'
release = version

language = 'en'

exclude_patterns = []

pygments_style = 'sphinx'

todo_include_todos = False

html_theme = 'sphinx_rtd_theme'
html_theme_options = {}

htmlhelp_basename = '{}doc'.format(project)
