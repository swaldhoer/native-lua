#!/usr/bin/env python
# encoding: utf-8

# SPDX-License-Identifier: MIT

# pylint: disable-msg=R0914

import os
import argparse
import logging
import sys
import pathlib
import subprocess
import shutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="sets the verbosity level"
    )
    parser.add_argument(
        "-c",
        "--compiler",
        action="append",
        required=True,
        help="specifies the compilers that should be tested",
    )
    parser.add_argument(
        "--simple-test",
        action="store_true",
        default=False,
        help="if specified, only simple tests are run.",
    )
    parser.add_argument(
        "--ltests", action="store_true", default=None, help="compile lua with ltests"
    )
    args = parser.parse_args()
    logger = logging.getLogger()
    if args.verbose == 0:
        logger.setLevel(logging.WARN)
    elif args.verbose == 1:
        logger.setLevel(logging.INFO)
    elif args.verbose >= 2:
        logger.setLevel(logging.DEBUG)
    repo_root = str(pathlib.Path(__file__).resolve().parent.parent)

    nr_errors = 0
    errors = {}
    base_cmd = [sys.executable, "waf"]
    prefix = os.path.join("build", "test")
    for compiler in args.compiler:
        cfg_args = ["configure", "--prefix={}".format(prefix), "--include-tests"]
        if args.ltests:
            cfg_args.extend(["--ltests"])
        cmds = [
            cfg_args,
            ["uninstall_{}".format(compiler)],
            ["build_{}".format(compiler)],
            ["install_{}".format(compiler)],
        ]
        for cmd in cmds:
            run_cmd = base_cmd + cmd
            logging.debug("running %s in %s", " ".join(run_cmd), repo_root)
            proc = subprocess.Popen(args=run_cmd, cwd=repo_root)
            proc.communicate()
            if proc.returncode:
                err_msg = "{} failed".format(cmd)
                logging.error(err_msg)
                nr_errors = nr_errors + 1
                errors.update({nr_errors: err_msg + " (command: {})".format(run_cmd)})
            else:
                suc_msg = "{} successfull".format(cmd)
                logging.info(suc_msg)

        logging.debug("searching lua")
        try:
            lua_exe = shutil.which("lua", path=os.path.join(repo_root, prefix, "bin"))
        except AttributeError:
            import distutils.spawn

            logging.warning("Falling back to distutils (instead of using shutil).")
            lua_exe = distutils.spawn.find_executable(
                "lua", path=os.path.join(repo_root, prefix, "bin")
            )
        if lua_exe is None:
            nr_errors = nr_errors + 1
            errors.update({nr_errors: "lua executable could not be found"})
        else:
            logging.debug("found lua: %s", lua_exe)

        test_cwd = str(os.path.join(repo_root, "build", compiler, "tests"))
        if os.path.isdir(test_cwd) and lua_exe:
            cmd = [lua_exe]
            if args.simple_test:
                cmd.extend(['-e"_U=true"'])
            cmd.extend(["all.lua"])
            cmd = " ".join(cmd)
            logging.debug("running %s in %s", cmd, test_cwd)
            proc = subprocess.Popen(args=cmd, cwd=test_cwd, shell=True)
            proc.communicate()
            if proc.returncode:
                err_msg = "error during testing {} build".format(compiler)
                logging.error(err_msg)
                nr_errors = nr_errors + 1
                errors.update({nr_errors: err_msg})
            else:
                logging.info("ok")
        else:
            err_msg = "misc error during testing {} build".format(compiler)
            logging.error(err_msg)
            nr_errors = nr_errors + 1
            errors.update({nr_errors: err_msg})
    # all tests are done
    if nr_errors:
        print("\n-----")
        for err in errors.items():
            print(err)
    sys.exit(nr_errors)


if __name__ == "__main__":
    main()
