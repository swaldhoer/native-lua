#!/usr/bin/env python
# encoding: utf-8

# SPDX-License-Identifier: MIT

from waflib import Utils


def configure(conf):
    if not conf.env.DOT:
        conf.find_program("dot", var="DOT")
        cmd = Utils.subst_vars("${DOT} -V", conf.env).split()
        proc = Utils.subprocess.Popen(cmd, stderr=Utils.subprocess.PIPE)
        try:
            conf.env.DOT_VERSION = " ".join(
                proc.communicate()[1].decode("utf-8").split()[4:]
            )
        except IndexError:
            conf.env.DOT_VERSION = "unknown"
