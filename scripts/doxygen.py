#!/usr/bin/env python
# encoding: utf-8

# SPDX-License-Identifier: MIT

import os

from waflib import Task, TaskGen, Utils, Logs


class DoxygenTask(Task.Task):
    color = "BLUE"

    vars = ["DOXYGEN_CONFIGURATION"]

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
    config = self.path.find_resource(self.conf)
    source_files = [config]
    cfg_lines = config.read().splitlines()
    setting = {}
    current_key = None
    while cfg_lines:
        cfg = cfg_lines.pop(0)
        if cfg.startswith("#") or cfg == "":
            continue
        d_set = [i.strip() for i in cfg.split("=")]
        if len(d_set) > 1:
            current_key = d_set[0]
        if not current_key:
            continue
        if current_key not in setting:
            setting[current_key] = []
        try:
            setting[current_key].append(d_set[1].replace("\\", "").strip())
        except IndexError:
            setting[current_key].append(d_set[0].replace("\\", "").strip())
    self.env.append_unique("DOXYGEN_CONFIGURATION", [setting])
    self.create_task("DoxygenTask", src=source_files)


def configure(conf):
    conf.find_program("doxygen", var="DOXYGEN")
    try:
        conf.env.DOXYGEN_VERSION = conf.cmd_and_log(
            Utils.subst_vars("${DOXYGEN} --version", conf.env).split()
        ).strip()
    except IndexError:
        conf.env.DOXYGEN_VERSION = "unknown"

    conf.load("dot", os.path.dirname(os.path.realpath(__file__)))
