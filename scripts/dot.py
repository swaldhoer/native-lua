#!/usr/bin/env python
# encoding: utf-8

# SPDX-License-Identifier: MIT

from waflib import Utils


def configure(cnf):
    if not cnf.env.DOT:
        cnf.find_program("dot", var="DOT")
        cmd = Utils.subst_vars("${DOT} -V", cnf.env).split()
        proc = Utils.subprocess.Popen(cmd, stderr=Utils.subprocess.PIPE)
        try:
            cnf.env.DOT_VERSION = " ".join(
                proc.communicate()[1].decode("utf-8").split()[4:]
            )
        except IndexError:
            cnf.env.DOT_VERSION = "unknown"
