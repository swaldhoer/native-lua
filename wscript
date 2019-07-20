#!/usr/bin/env python
# encoding: utf-8

# SPDX-License-Identifier: MIT

# pylint: disable=unused-variable

import os
import re

from waflib import Logs, Utils, Options, Context
from waflib.Tools.compiler_c import c_compiler
from waflib.Build import BuildContext, CleanContext, ListContext, StepContext
from waflib.Build import InstallContext, UninstallContext

from waflib.Tools.gnu_dirs import gnuopts

# man1 is missing waf gnu_dirs implementation
gnuopts += "mandir1, manual pages, ${DATAROOTDIR}/man1\n"

VERSION = "0.0.1"
APPNAME = "lua"
top = "."  # pylint: disable=C0103
out = "build"  # pylint: disable=C0103

Context.Context.line_just = 45

host_os = Utils.unversioned_sys_platform()  # pylint: disable=C0103

plat_comp = c_compiler["default"]  # pylint: disable=C0103
if c_compiler.get(host_os):
    plat_comp = c_compiler[host_os]  # pylint: disable=C0103
else:
    # add host compilers to compiler list. We need to do this, in order that we
    # use c_compiler[host_os] everywhere we need it.
    c_compiler[host_os] = plat_comp

for x in plat_comp:
    for y in (
        BuildContext,
        CleanContext,
        ListContext,
        StepContext,
        InstallContext,
        UninstallContext,
    ):
        name = y.__name__.replace("Context", "").lower()

        class Tmp(y):
            __doc__ = y.__doc__ + " ({})".format(x)
            cmd = name + "_" + x
            variant = x


if host_os == "win32":
    os.environ["PREFIX"] = os.path.join(
        os.environ.get("LOCALAPPDATA"), "Programs", "lua"
    )


def options(opt):
    opt.parser.remove_option("--top")
    opt.parser.remove_option("--out")
    opt.load("compiler_c")
    opt.load("python")
    opt.parser.remove_option("--nopyc")
    opt.parser.remove_option("--nopyo")
    opt.parser.remove_option("--nopycache")
    opt.parser.remove_option("--pythondir")
    opt.parser.remove_option("--pythonarchdir")
    opt.load("gnu_dirs")
    opt.parser.remove_option("--oldincludedir")
    opt.parser.remove_option("--dvidir")
    opt.parser.remove_option("--pdfdir")
    opt.parser.remove_option("--infodir")
    opt.parser.remove_option("--psdir")
    opt.parser.remove_option("--localedir")
    opt_gr = opt.get_option_group("Installation directories")
    opt_gr.add_option(
        "--man1dir",
        action="store",
        default="${DATAROOTDIR}/man1",
        help="system manual pages [DATAROOTDIR/man1]",
        dest="MAN1DIR",
    )
    opt.add_option(
        "--confcache",
        dest="confcache",
        default=0,
        action="count",
        help="Use a configuration cache",
    )
    opt.add_option(
        "--include-tests",
        dest="include_tests",
        default=False,
        action="store_true",
        help="Include test files",
    )
    opt.add_option(
        "--c-std",
        dest="c_standard",
        default="c99",
        choices=["c89", "c99"],
        help="Specify C-standard to be used. 'c99' is default. 'c99' will "
        "be replaced by 'gnu99' for gcc, xlc and icc. 'c99' will be "
        "replaced by 'c++14' for msvc. 'c89' is passed verbatim for "
        "gcc, xlc, icc and clang. 'c89' will be replaced by 'c++14' "
        " for msvc.",
    )
    opt.add_option(
        "--ltests",
        dest="ltests",
        default=False,
        action="store_true",
        help="Building with 'ltests'",
    )
    opt.add_option(
        "--generic",
        dest="generic",
        default=False,
        action="store_true",
        help="Build generic on the host " "platform. This is not supported on win32.",
    )


def configure(cnf):  # pylint: disable=R0912
    """Basic configuration of the project based on the operating system and
    the available compilers.
    """
    print("-" * (Context.Context.line_just + 1) + ":")
    cnf.load("python")
    cnf.check_python_version((2, 7))

    cnf.find_program("sphinx-build", var="SPHINX_BUILD", mandatory=False)
    cnf.check_python_module("sphinx_rtd_theme")
    if not cnf.env.SPHINX_BUILD:
        Logs.warn("Documentation build will not be available.")
    else:
        cnf.env.docs_out = os.path.join(out, "docs")

    print("-" * (Context.Context.line_just + 1) + ":")
    cnf.env.lua_src_version = tuple(
        cnf.path.find_node("LUA_VERSION").read().splitlines()[0].split(".")
    )
    cnf.env.lua_tests_version = tuple(
        cnf.path.find_node("LUA_TESTS_VERSION").read().splitlines()[0].split(".")
    )
    cnf.msg("Lua version", ".".join(cnf.env.lua_src_version))
    cnf.msg("Lua tests version", ".".join(cnf.env.lua_tests_version))
    cnf.msg("Including tests", cnf.options.include_tests)
    cnf.msg("Using ltests", cnf.options.ltests)
    cnf.env.generic = cnf.options.generic
    cnf.msg("Generic", cnf.env.generic)

    def get_c_standard(env_name, c_std):
        """Define C standard for each compiler"""
        c_std_string = None
        if env_name in ("gcc", "xlc", "icc"):
            pref = "-std="
            if c_std == "c89":
                c_std_string = "{}c89".format(pref)
            if c_std == "c99":
                c_std_string = "{}gnu99".format(pref)
        elif env_name == "clang":
            c_std_string = "-std={}".format(c_std)
        elif env_name == "msvc":
            c_std_string = "/std:c++14"
        return c_std_string or (cnf.fatal("Could not set C-standard"))

    def set_new_basic_env(env_name):
        """Create a new environment based on the base environment"""
        cnf.setenv("")
        tmp_env = cnf.env.derive()
        tmp_env.detach()
        cnf.setenv(env_name, tmp_env)
        cnf.env.env_name = env_name
        c_compiler[host_os] = [cnf.env.env_name]
        cnf.env.c_standard = get_c_standard(cnf.env.env_name, cnf.env.c_standard)
        cnf.path.get_bld().make_node(env_name).mkdir()

    def check_libs(*libs):
        for lib in libs:
            cnf.check(lib=lib, uselib_store=lib.upper())

    cnf.setenv("")
    cnf.env.host_os = host_os
    cnf.env.c_standard = cnf.options.c_standard
    cnf.env.include_tests = cnf.options.include_tests
    cnf.env.ltests = cnf.options.ltests
    cnf.load("gnu_dirs")
    cnf.env.MAN1DIR = Utils.subst_vars(cnf.options.MAN1DIR, cnf.env)

    min_c = "#include<stdio.h>\nint main() {\n    return 0;\n}\n"

    if cnf.options.c_standard == "c89":
        Logs.warn("C89 does not guarantee 64-bit integers for Lua.")
        Logs.warn("Adding define: LUA_USE_C89")  # TODO
        if host_os == "win32":
            Logs.warn("This will NOT effect msvc-builds on win32.")
    cnf.msg("C standard", cnf.options.c_standard)

    platform_compilers = []
    failed_platform_compilers = []
    if cnf.options.generic:
        if host_os == "win32":
            Logs.info("Generic build uses msvc on win32")
            cnf.env.WAF_CONFIG_H_PRELUDE = (
                "#if defined(_MSC_VER) && defined(_MSC_FULL_VER)\n"
                "#pragma warning(disable: 4242 4820 4668 4710 4711)\n"
                "#endif"
            )
            cnf.write_config_header("config.h")
            try:  # msvc
                set_new_basic_env("msvc")
                cnf.load("compiler_c")
                cnf.env.CFLAGS = ["/nologo", cnf.env.c_standard, "/O2", "/Wall"]
                cnf.env.CFLAGS += ["/FI" + cnf.env.cfg_files[0]]
                cnf.check_cc(fragment=min_c, execute=True)
                platform_compilers.append(cnf.env.env_name)
                cnf.msg("Manifest", cnf.env.MSVC_MANIFEST)
            except BaseException:
                failed_platform_compilers.append(cnf.env.env_name)
        else:
            try:
                # generic build only for gcc
                Logs.info(
                    "Generic build on {} with gcc".format(
                        Utils.unversioned_sys_platform()
                    )
                )
                set_new_basic_env("gcc")
                cnf.load("compiler_c")
                cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
                cnf.check_cc(fragment=min_c, execute=True)
                check_libs("m")
                platform_compilers.append(cnf.env.env_name)
            except BaseException:
                failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == "aix":
        try:  # xlc
            set_new_basic_env("xlc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-brtl,-bexpall"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # gcc
            # when compling with gcc, the xlc linker must still be used
            set_new_basic_env("gcc")
            cnf.env.LINK_CC = "xlc"
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-brtl,-bexpall"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env("gcc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-brtl,-bexpall"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os in ("netbsd", "openbsd"):
        try:  # gcc
            set_new_basic_env("gcc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == "freebsd":
        try:  # gcc
            set_new_basic_env("gcc")
            cnf.load("compiler_c")
            cnf.env.CC_VERSION_MAJOR = cnf.env.CC_VERSION[0]
            rpath = "/usr/local/lib/gcc" + cnf.env.CC_VERSION_MAJOR
            if not os.path.isdir(rpath):
                Logs.warn(
                    "Could not validate rpath, as path {} "
                    "does not exist".format(rpath)
                )
            else:
                cnf.env.append_unique("RPATH", rpath)
                cnf.msg("RPATH", cnf.env.RPATH[0])
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "readline")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            cnf.env.append_unique("INCLUDES", "/usr/local/include")
            cnf.env.append_unique("INCLUDES", "/usr/local/include/readline")
            cnf.env.append_unique("LIBPATH", "/usr/local/lib")
            check_libs("m", "readline")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == "linux":
        try:  # gcc
            set_new_basic_env("gcc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl", "readline")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl", "readline")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # icc
            set_new_basic_env("icc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl", "readline")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == "darwin":
        try:  # gcc
            set_new_basic_env("gcc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "readline")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            # cnf.env.LINKFLAGS = ['-Wl,-export_dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "readline")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == "win32":
        cnf.env.WAF_CONFIG_H_PRELUDE = (
            "#if defined(_MSC_VER) && defined(_MSC_FULL_VER)\n"
            "#pragma warning(disable: 4242 4820 4668 4710 4711)\n"
            "#endif"
        )
        cnf.write_config_header("config.h")
        try:  # msvc
            set_new_basic_env("msvc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = ["/nologo", cnf.env.c_standard, "/O2", "/Wall"]
            cnf.env.CFLAGS += ["/FI" + cnf.env.cfg_files[0]]
            cnf.check_cc(fragment=min_c, execute=True)
            platform_compilers.append(cnf.env.env_name)
            cnf.msg("Manifest", cnf.env.MSVC_MANIFEST)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # gcc
            set_new_basic_env("gcc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.check_cc(fragment=min_c, execute=True)
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == "cygwin":
        try:  # gcc
            set_new_basic_env("gcc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,--export-all-symbols"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == "solaris":
        try:  # gcc
            set_new_basic_env("gcc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # gcc
            set_new_basic_env("clang")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    else:
        Logs.warn("Building generic for platform: {}".format(host_os))

    if not platform_compilers:
        cnf.fatal(
            "Could not configure a single C compiler (tried: {}).\
            ".format(
                failed_platform_compilers
            )
        )
    if failed_platform_compilers:
        Logs.warn(
            "Could not configure the following compilers: {}".format(
                ", ".join(failed_platform_compilers)
            )
        )

    c_compiler[host_os] = platform_compilers
    cnf.msg("Configured compilers", ", ".join(c_compiler[host_os]))


def build(bld):
    """Wrapper for the compiler specific build"""
    if not bld.variant:
        if bld.cmd == "clean":
            Logs.warn("Cleaning for all platforms")
            Options.commands = ["clean_{}".format(t_cc) for t_cc in c_compiler[host_os]]
            Options.commands.append("clean_doc")
            return
    if bld.cmd == "build":
        bld.fatal(
            "Use a build variant: {}".format(
                " ".join("build_" + t_cc for t_cc in c_compiler[host_os])
            )
        )

    bld.clean_files = bld.bldnode.ant_glob(
        "**", excl=".lock* config.log c4che/* build.log", quiet=True, generator=True
    )

    if Utils.is_win32:
        if bld.variant == "gcc":
            # the DLL produced by gcc is already installed to ${BINDIR}
            pass
        if bld.variant == "msvc":
            bininst = bld.path.get_bld().ant_glob("*.dll **/*.manifest")
            libinst = []
            if bld.env.MSVC_MANIFEST:
                bininst += bld.path.get_bld().ant_glob("**/*.manifest")
                libinst += bld.path.get_bld().ant_glob("**/*dll.manifest")
            bld.install_files("${BINDIR}", bininst)
            bld.install_files("${LIBDIR}", libinst)
    else:
        # man files do not make sense on win32
        bld.install_files(
            "${MAN}", bld.path.find_node(os.path.join("docs", "man", "lua.1"))
        )
        bld.install_files(
            "${MAN1}", bld.path.find_node(os.path.join("docs", "man1", "luac.1"))
        )
    include_files = [
        bld.path.find_node(os.path.join("src", "lua.h")),
        bld.path.find_node(os.path.join("src", "luaconf.h")),
        bld.path.find_node(os.path.join("src", "lualib.h")),
        bld.path.find_node(os.path.join("src", "lauxlib.h")),
        bld.path.find_node(os.path.join("src", "lua.hpp")),
    ]
    for incfile in include_files:
        bld.install_files("${INCLUDEDIR}", incfile)

    bld.env.src_basepath = "src"
    bld.env.sources = " ".join(
        [
            os.path.join(bld.env.src_basepath, "lapi.c"),
            os.path.join(bld.env.src_basepath, "lcode.c"),
            os.path.join(bld.env.src_basepath, "ldo.c"),
            os.path.join(bld.env.src_basepath, "lctype.c"),
            os.path.join(bld.env.src_basepath, "ldebug.c"),
            os.path.join(bld.env.src_basepath, "ldump.c"),
            os.path.join(bld.env.src_basepath, "lfunc.c"),
            os.path.join(bld.env.src_basepath, "lgc.c"),
            os.path.join(bld.env.src_basepath, "llex.c"),
            os.path.join(bld.env.src_basepath, "lmem.c"),
            os.path.join(bld.env.src_basepath, "lobject.c"),
            os.path.join(bld.env.src_basepath, "lopcodes.c"),
            os.path.join(bld.env.src_basepath, "lparser.c"),
            os.path.join(bld.env.src_basepath, "lstate.c"),
            os.path.join(bld.env.src_basepath, "lstring.c"),
            os.path.join(bld.env.src_basepath, "ltable.c"),
            os.path.join(bld.env.src_basepath, "ltm.c"),
            os.path.join(bld.env.src_basepath, "lundump.c"),
            os.path.join(bld.env.src_basepath, "lvm.c"),
            os.path.join(bld.env.src_basepath, "lzio.c"),
            os.path.join(bld.env.src_basepath, "lauxlib.c"),
            os.path.join(bld.env.src_basepath, "lbaselib.c"),
            os.path.join(bld.env.src_basepath, "lbitlib.c"),
            os.path.join(bld.env.src_basepath, "lcorolib.c"),
            os.path.join(bld.env.src_basepath, "ldblib.c"),
            os.path.join(bld.env.src_basepath, "liolib.c"),
            os.path.join(bld.env.src_basepath, "lmathlib.c"),
            os.path.join(bld.env.src_basepath, "loslib.c"),
            os.path.join(bld.env.src_basepath, "lstrlib.c"),
            os.path.join(bld.env.src_basepath, "ltablib.c"),
            os.path.join(bld.env.src_basepath, "lutf8lib.c"),
            os.path.join(bld.env.src_basepath, "loadlib.c"),
            os.path.join(bld.env.src_basepath, "linit.c"),
        ]
    )
    bld.env.source_interpreter = os.path.join(bld.env.src_basepath, "lua.c")
    bld.env.source_compiler = os.path.join(bld.env.src_basepath, "luac.c")

    bld.env.tests_basepath = "tests"
    bld.env.ltests_dir = os.path.join(bld.env.tests_basepath, "ltests")
    bld.env.ltests_sources = os.path.join(bld.env.ltests_dir, "ltests.c")
    test_files = bld.path.ant_glob(bld.env.tests_basepath + "/**/*.lua")
    bld.env.test_files = [t.path_from(bld.path) for t in test_files]
    bld.env.libs_path = os.path.join(bld.env.tests_basepath, "libs")
    bld.env.test_sources = [
        os.path.join(bld.env.libs_path, "lib1.c"),
        os.path.join(bld.env.libs_path, "lib11.c"),
        os.path.join(bld.env.libs_path, "lib2.c"),
        os.path.join(bld.env.libs_path, "lib21.c"),
    ]
    if bld.env.generic:
        build_generic(bld)
    elif bld.env.host_os == "aix":
        build_aix(bld)
    elif bld.env.host_os in ("netbsd", "openbsd"):
        build_netbsd_or_openbsd(bld)
    elif bld.env.host_os == "freebsd":
        build_freebsd(bld)
    elif bld.env.host_os == "linux":
        build_linux(bld)
    elif bld.env.host_os == "darwin":
        build_darwin(bld)
    elif bld.env.host_os == "win32":
        build_win32(bld)
    elif bld.env.host_os == "cygwin":
        build_cygwin(bld)
    elif bld.env.host_os == "solaris":
        bld.cygwin(bld)
    else:
        bld.fatal("currently not supported platform")

    if bld.env.include_tests:
        bld(
            features="subst",
            source=bld.env.test_files,
            target=bld.env.test_files,
            is_copy=True,
        )


def build_generic(bld):
    use = ["M"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2"]
    defines_tests = []
    cflags = []
    includes = []
    if bld.env.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.env.ltests:
        use_ltests += ["LTESTS"]
        cflags += ["-g"]
        defines += ['LUA_USER_H="ltests.h"']
        includes += [bld.env.ltests_dir]
        bld.objects(
            source=bld.env.ltests_sources,
            defines=defines,
            cflags=cflags,
            includes=[bld.env.ltests_dir, bld.env.src_basepath],
            name="LTESTS",
        )

    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests,
        includes=includes,
        name="static-lua-library",
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        defines=defines,
        cflags=cflags,
        includes=includes,
        use=["static-lua-library"] + use + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        defines=defines,
        cflags=cflags,
        includes=includes,
        use=["static-lua-library"] + use + use_ltests,
    )

    if bld.env.include_tests:
        bld.path.get_bld().make_node(bld.env.tests_basepath + "/libs/P1").mkdir()
        for tst_src in bld.env.test_sources:
            outfile = re.match(".*?([0-9]+.c)$", tst_src).group(1).split(".")[0]
            outfile = bld.env.tests_basepath + "/libs/" + outfile
            bld.shlib(
                source=tst_src,
                target=outfile,
                defines=defines_tests,
                includes=os.path.abspath(
                    os.path.join(bld.path.abspath(), bld.env.src_basepath)
                ),
            )
        bld(
            features="subst",
            source=bld.env.tests_basepath + "/libs/lib2.so",
            target=bld.env.tests_basepath + "/libs/lib2-v2.so",
            is_copy=True,
        )


def build_aix(bld):
    use = ["M", "DL"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_POSIX", "LUA_USE_DLOPEN"]
    defines_tests = []
    cflags = []
    includes = []
    bld.fatal("TODO")


def build_netbsd_or_openbsd(bld):
    use = ["M"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_POSIX", "LUA_USE_DLOPEN"]
    defines_tests = []
    cflags = []
    includes = []
    bld.fatal("TODO")


def build_freebsd(bld):
    use = ["M", "READLINE"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_LINUX"]
    defines_tests = []
    cflags = []
    includes = []
    if bld.env.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.env.ltests:
        use_ltests += ["LTESTS"]
        cflags += ["-g"]
        defines += ['LUA_USER_H="ltests.h"']
        includes += [bld.env.ltests_dir]
        bld.objects(
            source=bld.env.ltests_sources,
            defines=defines,
            cflags=cflags,
            includes=[bld.env.ltests_dir, bld.env.src_basepath],
            name="LTESTS",
        )

    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests,
        includes=includes,
        name="static-lua-library",
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        defines=defines,
        cflags=cflags,
        includes=includes,
        use=["static-lua-library"] + use + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        defines=defines,
        cflags=cflags,
        includes=includes,
        use=["static-lua-library"] + use + use_ltests,
    )

    if bld.env.include_tests:
        bld.path.get_bld().make_node(bld.env.tests_basepath + "/libs/P1").mkdir()
        for tst_src in bld.env.test_sources:
            outfile = re.match(".*?([0-9]+.c)$", tst_src).group(1).split(".")[0]
            outfile = bld.env.tests_basepath + "/libs/" + outfile
            bld.shlib(
                source=tst_src,
                target=outfile,
                defines=defines_tests,
                includes=os.path.abspath(
                    os.path.join(bld.path.abspath(), bld.env.src_basepath)
                ),
            )
        bld(
            features="subst",
            source=bld.env.tests_basepath + "/libs/lib2.so",
            target=bld.env.tests_basepath + "/libs/lib2-v2.so",
            is_copy=True,
        )


def build_linux(bld):
    use = ["M", "DL", "READLINE"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_LINUX"]
    defines_tests = []
    cflags = []
    includes = []
    if bld.env.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.env.ltests:
        use_ltests += ["LTESTS"]
        cflags += ["-g"]
        defines += ['LUA_USER_H="ltests.h"']
        includes += [bld.env.ltests_dir]
        bld.objects(
            source=bld.env.ltests_sources,
            defines=defines,
            cflags=cflags,
            includes=[bld.env.ltests_dir, bld.env.src_basepath],
            name="LTESTS",
        )

    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests,
        includes=includes,
        name="static-lua-library",
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        defines=defines,
        cflags=cflags,
        includes=includes,
        use=["static-lua-library"] + use + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        defines=defines,
        cflags=cflags,
        includes=includes,
        use=["static-lua-library"] + use + use_ltests,
    )

    if bld.env.include_tests:
        bld.path.get_bld().make_node(bld.env.tests_basepath + "/libs/P1").mkdir()
        for tst_src in bld.env.test_sources:
            outfile = re.match(".*?([0-9]+.c)$", tst_src).group(1).split(".")[0]
            outfile = bld.env.tests_basepath + "/libs/" + outfile
            bld.shlib(
                source=tst_src,
                target=outfile,
                defines=defines_tests,
                includes=os.path.abspath(
                    os.path.join(bld.path.abspath(), bld.env.src_basepath)
                ),
            )
        bld(
            features="subst",
            source=bld.env.tests_basepath + "/libs/lib2.so",
            target=bld.env.tests_basepath + "/libs/lib2-v2.so",
            is_copy=True,
        )


def build_darwin(bld):
    use = ["M", "READLINE"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_MACOSX"]
    defines_tests = []
    cflags = []
    includes = []
    if bld.env.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.env.ltests:
        use_ltests += ["LTESTS"]
        cflags += ["-g"]
        defines += ['LUA_USER_H="ltests.h"']
        includes += [bld.env.ltests_dir]
        bld.objects(
            source=bld.env.ltests_sources,
            defines=defines,
            cflags=cflags,
            includes=[bld.env.ltests_dir, bld.env.src_basepath],
            name="LTESTS",
        )

    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests,
        includes=includes,
        name="static-lua-library",
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        defines=defines,
        cflags=cflags,
        includes=includes,
        use=["static-lua-library"] + use + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        defines=defines,
        cflags=cflags,
        includes=includes,
        use=["static-lua-library"] + use + use_ltests,
    )

    if bld.env.include_tests:
        bld.path.get_bld().make_node(bld.env.tests_basepath + "/libs/P1").mkdir()
        for tst_src in bld.env.test_sources:
            outfile = re.match(".*?([0-9]+.c)$", tst_src).group(1).split(".")[0]
            outfile = bld.env.tests_basepath + "/libs/" + outfile
            bld.shlib(
                source=tst_src,
                target=outfile,
                defines=defines_tests,
                includes=os.path.abspath(
                    os.path.join(bld.path.abspath(), bld.env.src_basepath)
                ),
            )
        if bld.env.CC_NAME == "gcc":
            ext = ".so"
        elif bld.env.CC_NAME == "clang":
            ext = ".dylib"
        bld(
            features="subst",
            source=bld.env.tests_basepath + "/libs/lib2" + ext,
            target=bld.env.tests_basepath + "/libs/lib2-v2" + ext,
            is_copy=True,
        )


def build_win32(bld):
    """Building on win32 platform
    Useable compilers are:
    - msvc
    - gcc
    - clang
    """

    def build_win32_msvc():
        """Building on win32 with msvc"""
        defines = ["LUA_COMPAT_5_2", "_WIN32"]
        bld.stlib(
            source=bld.env.sources,
            target="lua",
            defines=defines,
            name="static-lua-library",
        )

        bld.shlib(
            source=bld.env.sources,
            target="luadll",
            defines=defines + ["LUA_BUILD_AS_DLL"],
            name="shared-lua-library",
        )

        bld.program(
            source=bld.env.source_interpreter,
            target="lua",
            defines=defines,
            use=["shared-lua-library"],
        )

        bld.program(
            source=bld.env.source_compiler,
            target="luac",
            defines=defines,
            use=["static-lua-library"],
        )

    def build_win32_gcc():
        """Building on win32 with gcc"""
        use = ["M"]
        use_ltests = []
        defines = ["LUA_COMPAT_5_2", "_WIN32"]
        defines_tests = []
        cflags = []
        includes = []
        bld.stlib(
            source=bld.env.sources,
            target="lua",
            defines=defines,
            name="static-lua-library",
        )
        bld.shlib(
            source=bld.env.sources,
            target="luadll",
            defines=defines + ["LUA_BUILD_AS_DLL"],
            name="shared-lua-library",
        )
        bld.program(
            source=bld.env.source_interpreter,
            target="lua",
            use=["shared-lua-library"] + use,
        )
        bld.program(
            source=bld.env.source_compiler,
            target="luac",
            defines=defines,
            use=["static-lua-library"] + use,
        )

    def build_win32_clang():
        """Building on win32 with clang"""
        use = ["M"]
        use_ltests = []
        defines = ["LUA_COMPAT_5_2", "_WIN32"]
        defines_tests = []
        cflags = []
        includes = []
        bld.stlib(
            source=bld.env.sources,
            target="lua",
            defines=defines,
            name="static-lua-library",
        )
        bld.shlib(
            source=bld.env.sources,
            target="luadll",
            defines=defines + ["LUA_BUILD_AS_DLL"],
            name="shared-lua-library",
        )
        bld.program(
            source=bld.env.source_interpreter,
            target="lua",
            use=["shared-lua-library"] + use,
        )
        bld.program(
            source=bld.env.source_compiler,
            target="luac",
            defines=defines,
            use=["static-lua-library"] + use,
        )

    if bld.env.CC_NAME == "msvc":
        build_win32_msvc()
    elif bld.env.CC_NAME == "gcc":
        build_win32_gcc()
    elif bld.env.CC_NAME == "clang":
        build_win32_clang()


def build_cygwin(bld):
    """Building on win32-cygwin with gcc"""
    use = ["M"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_LINUX"]
    defines_tests = []
    cflags = []
    includes = []
    bld.stlib(
        source=bld.env.sources, target="lua", defines=defines, name="static-lua-library"
    )
    bld.shlib(
        source=bld.env.sources,
        target="luadll",
        defines=defines + ["LUA_BUILD_AS_DLL"],
        name="shared-lua-library",
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        use=["shared-lua-library"] + use,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        defines=defines,
        use=["static-lua-library"] + use,
    )


def build_solaris(bld):
    use = ["M", "DL"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_POSIX", "LUA_USE_DLOPEN", "_REENTRANT"]
    defines_tests = []
    cflags = []
    includes = []
    if bld.env.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.env.ltests:
        use_ltests += ["LTESTS"]
        cflags += ["-g"]
        defines += ['LUA_USER_H="ltests.h"']
        includes += [bld.env.ltests_dir]
        bld.objects(
            source=bld.env.ltests_sources,
            defines=defines,
            cflags=cflags,
            includes=[bld.env.ltests_dir, bld.env.src_basepath],
            name="LTESTS",
        )

    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests,
        includes=includes,
        name="static-lua-library",
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        defines=defines,
        cflags=cflags,
        includes=includes,
        use=["static-lua-library"] + use + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        defines=defines,
        cflags=cflags,
        includes=includes,
        use=["static-lua-library"] + use + use_ltests,
    )

    if bld.env.include_tests:
        bld.path.get_bld().make_node(bld.env.tests_basepath + "/libs/P1").mkdir()
        for tst_src in bld.env.test_sources:
            outfile = re.match(".*?([0-9]+.c)$", tst_src).group(1).split(".")[0]
            outfile = bld.env.tests_basepath + "/libs/" + outfile
            bld.shlib(
                source=tst_src,
                target=outfile,
                defines=defines_tests,
                includes=os.path.abspath(
                    os.path.join(bld.path.abspath(), bld.env.src_basepath)
                ),
            )
        bld(
            features="subst",
            source=bld.env.tests_basepath + "/libs/lib2.so",
            target=bld.env.tests_basepath + "/libs/lib2-v2.so",
            is_copy=True,
        )


def build_doc(ctx):
    """builds the documentation"""
    # TODO needs a waf-style implementation
    ctx.cmd_and_log("sphinx-build -b html docs build/docs", output=Context.BOTH)


def clean_doc(ctx):
    """cleans the documentation"""
    # TODO needs a waf-style implementation
    doc_files = ctx.path.ant_glob(os.path.join("build", "docs", "**/*"))
    for doc_file in doc_files:
        doc_file.delete()
