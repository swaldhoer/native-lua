#!/usr/bin/env python3
# encoding: utf-8

# SPDX-License-Identifier: MIT

import argparse
import re
import shutil
import sys

from subprocess import Popen, PIPE

RE_VERSION = r"((\d+)\.(\d+)\.(\d+))"
VERSIONS = {
    "black": {"cmd": ("black", "--version"), "version": r"((\d+)\.([a-z0-9]{0,3}))"},
    "clang": {"cmd": ("clang", "--version")},
    "doxygen": {"cmd": ("doxygen", "--version")},
    "gcc": {"cmd": ("gcc", "--version")},
    "graphviz": {"cmd": ("dot", "-V")},
    "sphinx": {"cmd": ("sphinx-build", "--version")},
    "pylint": {"cmd": ("pylint", "--version"), "version": r"pylint\s*" + RE_VERSION},
    "python": {"cmd": (sys.executable, "--version")},
    "msvc": {"cmd": ("cl",)},
    "isort": {"cmd": ("isort", "--version")},
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tool",
        action="append",
        default=["python"],
        help="Tool version that should be displayed",
    )
    args = parser.parse_args()
    err = False
    for tool in args.tool:
        try:
            VERSIONS[tool]
        except KeyError:
            VERSIONS[tool] = {"cmd": (tool, "--version")}
        if not shutil.which(VERSIONS[tool]["cmd"][0]):
            err = True
            print(f"Could not find program '{VERSIONS[tool]['cmd'][0]}'.")
            continue
        # pylint: disable=consider-using-with
        proc = Popen(VERSIONS[tool]["cmd"], stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")
        version, m = "", False
        for i in (stdout, stderr):
            m = re.search(VERSIONS[tool].get("version", RE_VERSION), i)
            if m:
                version = m.group(1)
                break
        if proc.returncode or not m:
            err = True
            print(f"Could not determine version for {VERSIONS[tool]}.")
        print(f"{tool}: {version}")
    sys.exit(err)


if __name__ == "__main__":
    main()
