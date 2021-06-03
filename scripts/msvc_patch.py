#!/usr/bin/env python3
# encoding: utf-8

# SPDX-License-Identifier: MIT
import os

from waflib import TaskGen

USE_ABSOLUTE_INCPATHS = ["\\Microsoft Visual Studio\\", "\\Windows Kits\\"]


@TaskGen.feature("c")
@TaskGen.after_method("apply_incpaths")
def make_msvc_and_win_paths_absolute(self):
    incpaths_fixed = []
    for inc_path in self.env.INCPATHS:
        if any(i in inc_path for i in USE_ABSOLUTE_INCPATHS):
            incpaths_fixed.append(os.path.abspath(inc_path))
        else:
            incpaths_fixed.append(inc_path)
    self.env.INCPATHS = incpaths_fixed


def configure(conf):
    conf.msg("Use absolute include paths", True)
