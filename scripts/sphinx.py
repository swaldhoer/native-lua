#!/usr/bin/env python
# encoding: utf-8

# SPDX-License-Identifier: MIT

from waflib.Task import Task
from waflib.TaskGen import feature, extension


class SphinxTask(Task):
    color = "BLUE"
    run_str = "${SPHINX_BUILD} -b ${BUILDERNAME} -c ${CONFIG} ${INPUTDIR} ${OUTDIR}"

    def keyword(self):
        return "Compiling {} -> {}".format(self.env.CONFIG, self.env.OUTDIR)

    def post_run(self):
        nodes = self.generator.bld.path.get_bld().ant_glob("**/*", quiet=True)
        for i in nodes:
            self.generator.bld.node_sigs[i] = self.uid()
        return Task.post_run(self)


def configure(cnf):
    cnf.find_program("sphinx-build", var="SPHINX_BUILD")


@feature("sphinx")
def build_sphinx(self):
    if not getattr(self, "buildername", None):
        self.env.BUILDERNAME = "html"
    else:
        self.env.BUILDERNAME = self.buildername

    if not getattr(self, "confpy", None):
        confpy = self.path.find_node("conf.py")
    else:
        confpy = self.path.find_node(self.confpy)

    self.env.CONFIG = confpy.parent.abspath()

    self.env.INPUTDIR = self.source[0].parent.abspath()
    self.env.OUTDIR = self.path.get_bld().abspath()

    self.create_task("SphinxTask")


@extension(".rst")
def rst_hook(self, node):  # pylint: disable=W0613
    pass
