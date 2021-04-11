#!/usr/bin/env python3
# encoding: utf-8

# SPDX-License-Identifier: MIT

import os

from waflib import Utils
from waflib.Task import Task
from waflib.TaskGen import extension, feature


class SphinxTask(Task):
    color = "BLUE"

    vars = ["CONFIG_HASH"]

    run_str = (
        "${SPHINX_BUILD} -b ${BUILDERNAME} ${SPHINX_OPTIONS} -c ${CONFIG} "
        "${INPUTDIR} ${OUTDIR}"
    )

    def keyword(self):
        return "Compiling {} -> {}".format(self.env.CONFIG, self.env.OUTDIR)

    def post_run(self):
        nodes = self.generator.bld.path.get_bld().ant_glob(
            "**/*", excl=["**/_doxygen/**/*"], quiet=True
        )
        for i in nodes:
            self.generator.bld.node_sigs[i] = self.uid()
        return Task.post_run(self)


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
    if not confpy:
        self.bld.fatal("No valid conf.py found or found.")
    self.env.CONFIG_HASH = Utils.h_file(confpy.abspath())
    self.env.CONFIG = confpy.parent.abspath()

    self.env.INPUTDIR = self.source[0].parent.abspath()
    self.env.OUTDIR = self.path.get_bld().abspath()
    tgt = []
    for src in self.source:
        tgt.append(
            self.path.find_or_declare(
                os.path.join(
                    self.path.get_bld().abspath(),
                    os.sep.join(
                        list(
                            filter(
                                None,
                                src.relpath().replace(".rst", ".html").split(os.sep),
                            )
                        )[1:]
                    ),
                )
            )
        )
        tgt.append(
            self.path.find_or_declare(
                os.path.join(
                    self.path.get_bld().abspath(),
                    ".doctrees",
                    os.sep.join(
                        list(
                            filter(
                                None,
                                src.relpath().replace(".rst", ".doctree").split(os.sep),
                            )
                        )[1:]
                    ),
                )
            )
        )
        tgt.append(
            self.path.find_or_declare(
                os.path.join(
                    self.path.get_bld().abspath(),
                    "_sources",
                    os.sep.join(
                        list(
                            filter(
                                None,
                                src.relpath().replace(".rst", ".rst.txt").split(os.sep),
                            )
                        )[1:]
                    ),
                )
            )
        )
    tgt.extend(
        [
            self.path.find_or_declare(
                os.path.join(self.path.get_bld().abspath(), ".buildinfo")
            ),
            self.path.find_or_declare(
                os.path.join(self.path.get_bld().abspath(), "objects.inv")
            ),
            self.path.find_or_declare(
                os.path.join(self.path.get_bld().abspath(), "searchindex.js")
            ),
        ]
    )
    self.create_task("SphinxTask", src=self.source, tgt=tgt)


@extension(".rst")
def rst_hook(self, node):  # pylint: disable=unused-argument
    pass


def configure(conf):
    conf.find_program("sphinx-build", var="SPHINX_BUILD")
    cmd = Utils.subst_vars("${SPHINX_BUILD} --version", conf.env).split()
    try:
        conf.env.SPHINX_BUILD_VERSION = conf.cmd_and_log(cmd).strip().split(" ")[1]
    except IndexError:
        conf.env.SPHINX_BUILD_VERSION = "unknown"
    conf.env.append_unique("SPHINX_OPTIONS", [])

    conf.load("dot", tooldir=os.path.dirname(os.path.realpath(__file__)))
