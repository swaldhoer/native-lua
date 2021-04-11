#!/usr/bin/env python3
# encoding: utf-8

# SPDX-License-Identifier: MIT

from waflib import Context, Utils


def configure(conf):
    if not conf.env.DOT:
        conf.find_program("dot", var="DOT")
        cmd_out = conf.cmd_and_log(
            Utils.subst_vars("${DOT} -V", conf.env).split(),
            output=Context.STDOUT,
            quiet=Context.BOTH,
        )
        try:
            conf.env.DOT_VERSION = " ".join(cmd_out[1].decode("utf-8").split()[4:])
        except IndexError:
            conf.env.DOT_VERSION = "unknown"
