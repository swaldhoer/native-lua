#!/usr/bin/env python
# encoding: utf-8

# SPDX-License-Identifier: MIT

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


def configure(conf):
    conf.find_program("doxygen", var="DOXYGEN")
    conf.find_program("dot", var="DOT")
