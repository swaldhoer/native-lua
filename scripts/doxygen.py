#!/usr/bin/env python
# encoding: utf-8

# SPDX-License-Identifier: MIT

import os

from waflib import Task, TaskGen, Utils, Logs


class DoxygenTask(Task.Task):
    color = "BLUE"

    def run(self):
        cmd = Utils.subst_vars("${DOXYGEN}", self.env)
        cmd = [cmd, self.inputs[0].abspath()]
        proc = Utils.subprocess.Popen(
            cmd,
            stdout=Utils.subprocess.PIPE,
            stderr=Utils.subprocess.PIPE,
            cwd=self.inputs[0].parent.abspath(),
        )
        out, err = proc.communicate()
        print("out", out.decode("utf-8"))
        Logs.warn(err.decode("utf-8"))
        return proc.returncode


@TaskGen.feature("doxygen")
def process_doxy(self):
    self.create_task("DoxygenTask", self.path.find_resource(self.conf))


def configure(cnf):
    cnf.find_program("doxygen", var="DOXYGEN")
    cmd = Utils.subst_vars("${DOXYGEN} --version", cnf.env).split()
    try:
        cnf.env.DOXYGEN_VERSION = cnf.cmd_and_log(cmd).strip()
    except IndexError:
        cnf.env.DOXYGEN_VERSION = "unknown"
    cnf.load("dot", os.path.dirname(os.path.realpath(__file__)))
