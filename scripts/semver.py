#!/usr/bin/env python3
# encoding: utf-8

# SPDX-License-Identifier: MIT

import re

from waflib import TaskGen

# Regex for Semantic Versioning 2.0.0
# https://semver.org/spec/v2.0.0.html#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*"
    r"[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))"
    r"*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

ERR_MSG = (
    "Version information does not follow sematic versioning 2.0.0 ({})\n"
    "See https://semver.org/spec/v2.0.0.html for details."
)


@TaskGen.feature("*")
@TaskGen.before("process_rule")
def semver_check(self):
    is_semver = re.match(SEMVER_RE, self.env.VERSION)
    if not is_semver:
        self.bld.fatal(ERR_MSG.format(self.env.VERSION))


def configure(conf):
    if not conf.env.VERSION:
        conf.fatal("VERSION must be set prior to loading semver.")
    conf.start_msg("Validating version number")
    is_semver = re.match(SEMVER_RE, conf.env.VERSION)
    if not is_semver:
        conf.fatal(ERR_MSG.format(conf.env.VERSION))
    conf.end_msg(True)
