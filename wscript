#!/usr/bin/env python
# encoding: utf-8

# SPDX-License-Identifier: MIT

# pylint: disable=unused-variable

import os
import re
import json

from waflib import Logs, Utils, Options, Context, TaskGen
from waflib.Tools.compiler_c import c_compiler
from waflib.Build import BuildContext, CleanContext, ListContext, StepContext
from waflib.Build import InstallContext, UninstallContext


VERSION = "0.5.0-devel"
APPNAME = "lua"
top = "."  # pylint: disable=invalid-name
out = "build"  # pylint: disable=invalid-name

Context.Context.line_just = 45

USE_ABSOLUTE_INCPATHS = ["\\Microsoft Visual Studio\\", "\\Windows Kits\\"]


@TaskGen.feature("c")
@TaskGen.after_method("apply_incpaths")
def make_msvc_and_win_paths_absolute(self):
    incpaths_fixed = []
    for inc_path in self.env.INCPATHS:
        if any(i in inc_path for i in USE_ABSOLUTE_INCPATHS):
            incpaths_fixed.append(os.path.abspath(inc_path))
        else:
            incpaths_fixed.append(inc_path)
    self.env.INCPATHS = incpaths_fixed


host_os = Utils.unversioned_sys_platform()  # pylint: disable=invalid-name
plat_comp = c_compiler["default"]  # pylint: disable=invalid-name
if c_compiler.get(host_os):
    plat_comp = c_compiler[host_os]  # pylint: disable=invalid-name
else:
    # add host compilers to compiler list. We need to do this, in order that we
    # use c_compiler[host_os] everywhere we need it.
    c_compiler[host_os] = plat_comp

for x in plat_comp + ["docs"]:
    for y in (BuildContext, CleanContext):
        NAME = y.__name__.replace("Context", "").lower()

        class Tmp1(y):
            __doc__ = y.__doc__ + " ({})".format(x)
            cmd = NAME + "_" + x
            variant = x

    if x != "docs":
        for y in (ListContext, StepContext, InstallContext, UninstallContext):
            NAME = y.__name__.replace("Context", "").lower()

            class Tmp2(y):
                __doc__ = y.__doc__ + " ({})".format(x)
                cmd = NAME + "_" + x
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
        "for msvc.",
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
        help="Build generic on the host platform. This is not supported on win32.",
    )


def configure(conf):  # pylint: disable=too-many-branches,too-many-locals
    """Basic configuration of the project based on the operating system and
    the available compilers.
    """

    conf.msg("Prefix", conf.env.PREFIX)
    conf.load("python")
    conf.check_python_version((3, 5))
    conf.env.define_key.remove("PYTHONDIR")
    conf.env.define_key.remove("PYTHONARCHDIR")

    conf.load("sphinx", tooldir="scripts")
    conf.load("doxygen", tooldir="scripts")

    # check that all version numbers match and the the version number adheres
    # to Semantic Versioning 2.0.0
    # https://semver.org/spec/v2.0.0.html#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
    sem_ver_re = re.compile(
        r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*"
        r"[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))"
        r"*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    )

    is_sem_ver = re.match(sem_ver_re, VERSION)
    if not is_sem_ver:
        conf.fatal(
            "Version information does not follow sematic versioning 2.0.0 ({})\n"
            "See https://semver.org/spec/v2.0.0.html for details.".format(VERSION)
        )

    base_err_msg = (
        "wscript's VERSION attribute ({}) and version information in file {} "
        "({}) do not match."
    )

    version_file = conf.path.find_node("VERSION")
    version_info = json.loads(version_file.read(encoding="utf-8"))
    version_file_ver = version_info["native Lua"]
    if not VERSION == version_file_ver:
        conf.fatal(base_err_msg.format(VERSION, version_file, version_file_ver))

    confpy_file = conf.path.find_node("docs/conf.py")
    confpy_txt = confpy_file.read(encoding="utf-8")
    confpy_file_ver = re.search(r'(version)( = )"(.{0,})"', confpy_txt).group(3)
    if not VERSION == confpy_file_ver:
        conf.fatal(base_err_msg.format(VERSION, confpy_file, confpy_file_ver))

    readme_file = conf.path.find_node("README.md")
    readme_txt = readme_file.read(encoding="utf-8")
    readme_file_ver = re.search(r"(based on native Lua )\((.{0,})\)", readme_txt).group(
        2
    )
    if not VERSION == readme_file_ver:
        conf.fatal(base_err_msg.format(VERSION, readme_file, readme_file_ver))

    start_file = conf.path.find_node("docs/start.rst")
    start_txt = start_file.read(encoding="utf-8")
    start_file_ver = re.search(r"(based on native Lua )\((.{0,})\)", start_txt).group(2)
    if not VERSION == readme_file_ver:
        conf.fatal(base_err_msg.format(VERSION, readme_file, readme_file_ver))

    doxygen_file = conf.path.find_node("docs/doxygen.conf")
    doxygen_txt = doxygen_file.read(encoding="utf-8")
    doxygen_file_ver = re.search(
        r'(PROJECT_NUMBER)(         = )"(.{0,})"', doxygen_txt
    ).group(3)
    if not VERSION == doxygen_file_ver:
        conf.fatal(base_err_msg.format(VERSION, doxygen_file, doxygen_file_ver))

    conf.env.lua_src_version = version_info["lua"]
    conf.env.lua_tests_version = version_info["tests"]
    conf.msg("native Lua version", VERSION)
    conf.msg("Lua version", conf.env.lua_src_version)
    conf.msg("Lua tests version", conf.env.lua_tests_version)
    conf.msg("Including tests", conf.options.include_tests)
    conf.msg("Using ltests", conf.options.ltests)
    conf.env.generic = conf.options.generic
    conf.msg("Generic", conf.env.generic)

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
        return c_std_string or (conf.fatal("Could not set C-standard"))

    def set_new_basic_env(env_name):
        """Create a new environment based on the base environment"""
        conf.setenv("")
        tmp_env = conf.env.derive()
        tmp_env.detach()
        conf.setenv(env_name, tmp_env)
        conf.env.env_name = env_name
        c_compiler[host_os] = [conf.env.env_name]
        conf.env.c_standard = get_c_standard(conf.env.env_name, conf.env.c_standard)
        conf.path.get_bld().make_node(env_name).mkdir()

    def check_libs(*libs):
        for lib in libs:
            conf.check(lib=lib, uselib_store=lib.upper())

    conf.setenv("")
    conf.env.host_os = host_os
    conf.env.c_standard = conf.options.c_standard
    conf.env.include_tests = conf.options.include_tests
    conf.env.ltests = conf.options.ltests
    conf.load("gnu_dirs")

    min_c = "#include<stdio.h>\nint main() {\n    return 0;\n}\n"

    if conf.options.c_standard == "c89":
        Logs.warn("C89 does not guarantee 64-bit integers for Lua.")
        Logs.warn("Adding define: LUA_USE_C89")  # TODO
        if host_os == "win32":
            Logs.warn("This will NOT effect msvc-builds on win32.")
    conf.msg("C standard", conf.options.c_standard)

    conf.env.WAF_CONFIG_H_PRELUDE = (
        '#define NATIVE_LUA_PRE_MSG "based on native Lua"\n'
        '#define NATIVE_LUA_VERSION "{}"\n'.format(VERSION) + ""
        '#define NATIVE_LUA_REPO "https://github.com/swaldhoer/native-lua"\n'
        '#define NATIVE_LUA_MSG " [" NATIVE_LUA_PRE_MSG " (" NATIVE_LUA_VERSION"), " NATIVE_LUA_REPO"]"\n\n'
    )
    platform_compilers = []
    failed_platform_compilers = []
    conf.write_config_header(configfile="waf_build_config.h")
    if conf.options.generic:
        if host_os == "win32":
            Logs.info("Generic build uses msvc on win32")
            try:  # msvc
                set_new_basic_env("msvc")
                conf.load("compiler_c")
                conf.env.CFLAGS = [
                    "/nologo",
                    conf.env.c_standard,
                    "/O2",
                    "/Wall",
                    "/Qspectre",
                ]
                conf.env.CFLAGS += ["/FI" + conf.env.cfg_files[0]]
                conf.env.CMCFLAGS = ["/Os"]
                conf.check_cc(fragment=min_c, execute=True)
                platform_compilers.append(conf.env.env_name)
                conf.msg("Manifest", conf.env.MSVC_MANIFEST)
            except BaseException:
                failed_platform_compilers.append(conf.env.env_name)
        else:
            try:
                # generic build only for gcc
                Logs.info(
                    "Generic build on {} with gcc".format(
                        Utils.unversioned_sys_platform()
                    )
                )
                set_new_basic_env("gcc")
                conf.load("compiler_c")
                conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
                conf.env.CMCFLAGS = ["-Os"]
                conf.check_cc(fragment=min_c, execute=True)
                check_libs("m")
                platform_compilers.append(conf.env.env_name)
            except BaseException:
                failed_platform_compilers.append(conf.env.env_name)
    elif host_os == "aix":
        try:  # xlc
            set_new_basic_env("xlc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-brtl,-bexpall"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # gcc
            # when compling with gcc, the xlc linker must still be used
            set_new_basic_env("gcc")
            conf.env.LINK_CC = "xlc"
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-brtl,-bexpall"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # clang
            set_new_basic_env("gcc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-brtl,-bexpall"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
    elif host_os == "openbsd":
        try:  # gcc
            set_new_basic_env("gcc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
    elif host_os == "netbsd":
        try:  # gcc
            set_new_basic_env("gcc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
    elif host_os == "freebsd":
        try:  # gcc
            set_new_basic_env("gcc")
            conf.load("compiler_c")
            conf.env.CC_VERSION_MAJOR = conf.env.CC_VERSION[0]
            rpath = "/usr/local/lib/gcc" + conf.env.CC_VERSION_MAJOR
            if not os.path.isdir(rpath):
                Logs.warn(
                    "Could not validate rpath, as path {} "
                    "does not exist".format(rpath)
                )
            else:
                conf.env.append_unique("RPATH", rpath)
                conf.msg("RPATH", conf.env.RPATH[0])
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl", "edit")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            conf.env.append_unique("INCLUDES", "/usr/include/edit")
            conf.env.append_unique("LIBPATH", "/usr/local/lib")
            check_libs("m", "dl", "edit")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
    elif host_os == "linux":
        try:  # gcc
            set_new_basic_env("gcc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl", "readline")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl", "readline")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # icc
            set_new_basic_env("icc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl", "readline")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
    elif host_os == "darwin":
        try:  # gcc
            set_new_basic_env("gcc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "readline")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "readline")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
    elif host_os == "win32":
        try:  # msvc
            set_new_basic_env("msvc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [
                "/nologo",
                conf.env.c_standard,
                "/O2",
                "/Wall",
                "/Qspectre",
            ]
            conf.env.CFLAGS += ["/FI" + conf.env.cfg_files[0]]
            conf.env.CMCFLAGS = ["/Os"]
            conf.check_cc(fragment=min_c, execute=True)
            platform_compilers.append(conf.env.env_name)
            conf.msg("Manifest", conf.env.MSVC_MANIFEST)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # gcc
            set_new_basic_env("gcc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            # these vars fix the luac build
            conf.env.cstlib_PATTERN = "%s.lib"
            conf.env.LINKFLAGS = []
            conf.env.STLIB_MARKER = ""
            conf.env.SHLIB_MARKER = ""
            # these vars fix the lua build
            conf.env.IMPLIB_ST = "-IMPLIB:%s"
            conf.env.implib_PATTERN = "%s.dll"
            conf.check_cc(fragment=min_c, execute=True)
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
    elif host_os == "cygwin":
        try:  # gcc
            set_new_basic_env("gcc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,--export-all-symbols"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,--export-all-symbols"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
    elif host_os == "solaris":
        try:  # gcc
            set_new_basic_env("gcc")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
        try:  # gcc
            set_new_basic_env("clang")
            conf.load("compiler_c")
            conf.env.CFLAGS = [conf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            conf.env.CMCFLAGS = ["-Os"]
            conf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            conf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "dl")
            platform_compilers.append(conf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(conf.env.env_name)
    else:
        Logs.warn("Building generic for platform: {}".format(host_os))

    if not platform_compilers:
        conf.fatal(
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
    conf.msg("Configured compilers", ", ".join(c_compiler[host_os]))


def build(bld):
    """Wrapper for the compiler specific build"""

    # check correct build commands
    if not bld.variant:
        if bld.cmd == "clean":
            Logs.warn("Cleaning for all platforms")
            Options.commands = ["clean_{}".format(t_cc) for t_cc in c_compiler[host_os]]
            Options.commands.append("clean_doc")
            return

    if bld.cmd == "build":
        bld.fatal(
            "Use a build variant: {}".format(
                " ".join("build_" + t_cc for t_cc in c_compiler[host_os] + ["docs"])
            )
        )

    bld.clean_files = bld.bldnode.ant_glob(
        "**", excl=".lock* config.log c4che/* build.log", quiet=True, generator=True
    )

    # check that the binary is available in PATH
    if bld.cmd.startswith("install"):
        bin_dir = Utils.subst_vars(bld.env.BINDIR, bld.env)
        if not any(
            [x if x == bin_dir else False for x in os.environ["PATH"].split(os.pathsep)]
        ):
            Logs.warn("lua is not in available in PATH.")
            Logs.warn("Add the following path to PATH: {}".format(bin_dir))

    # setup install files
    if Utils.is_win32:
        if bld.variant == "gcc":
            # the DLL produced by gcc is already installed to ${BINDIR}
            pass
        if bld.variant == "msvc":
            bininst = bld.path.get_bld().ant_glob("*.dll **/*.manifest", quiet=True)
            libinst = []
            if bld.env.MSVC_MANIFEST:
                bininst += bld.path.get_bld().ant_glob("**/*.manifest", quiet=True)
                libinst += bld.path.get_bld().ant_glob("**/*dll.manifest", quiet=True)
            bld.install_files("${BINDIR}", bininst)
            bld.install_files("${LIBDIR}", libinst)
    else:
        # man files do not make sense on win32
        bld.install_files(
            "${MANDIR}/man1",
            [
                bld.path.find_node(os.path.join("docs", "_static", "doc", "lua.1")),
                bld.path.find_node(os.path.join("docs", "_static", "doc", "luac.1")),
            ],
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

    # actual binary and documentation builds
    bld.env.append_unique("INCLUDES", bld.path.get_bld().parent.abspath())

    bld.env.src_basepath = "src"
    bld.env.sources = " ".join(
        [
            os.path.join(bld.env.src_basepath, "lapi.c"),
            os.path.join(bld.env.src_basepath, "ldo.c"),
            os.path.join(bld.env.src_basepath, "lctype.c"),
            os.path.join(bld.env.src_basepath, "ldebug.c"),
            os.path.join(bld.env.src_basepath, "ldump.c"),
            os.path.join(bld.env.src_basepath, "lfunc.c"),
            os.path.join(bld.env.src_basepath, "lgc.c"),
            os.path.join(bld.env.src_basepath, "lmem.c"),
            os.path.join(bld.env.src_basepath, "lobject.c"),
            os.path.join(bld.env.src_basepath, "lopcodes.c"),
            os.path.join(bld.env.src_basepath, "lstate.c"),
            os.path.join(bld.env.src_basepath, "lstring.c"),
            os.path.join(bld.env.src_basepath, "ltable.c"),
            os.path.join(bld.env.src_basepath, "ltm.c"),
            os.path.join(bld.env.src_basepath, "lundump.c"),
            os.path.join(bld.env.src_basepath, "lvm.c"),
            os.path.join(bld.env.src_basepath, "lzio.c"),
            os.path.join(bld.env.src_basepath, "lauxlib.c"),
            os.path.join(bld.env.src_basepath, "lbaselib.c"),
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
    bld.env.compiler_module_sources = [
        os.path.join(bld.env.src_basepath, "lcode.c"),
        os.path.join(bld.env.src_basepath, "llex.c"),
        os.path.join(bld.env.src_basepath, "lparser.c"),
    ]
    bld.env.source_interpreter = os.path.join(bld.env.src_basepath, "lua.c")
    bld.env.source_compiler = os.path.join(bld.env.src_basepath, "luac.c")

    bld.env.tests_basepath = "tests"
    bld.env.ltests_dir = os.path.join(bld.env.tests_basepath, "ltests")
    bld.env.ltests_sources = os.path.join(bld.env.ltests_dir, "ltests.c")
    test_files = bld.path.ant_glob(bld.env.tests_basepath + "/**/*.lua")
    bld.env.test_files = [t.path_from(bld.path) for t in test_files]
    bld.env.libs_path = os.path.join(bld.env.tests_basepath, "libs")
    bld.env.library_test = [
        (os.path.join(bld.env.libs_path, "lib1.c"), "1"),
        (os.path.join(bld.env.libs_path, "lib11.c"), "11"),
        (os.path.join(bld.env.libs_path, "lib2.c"), "2"),
        (os.path.join(bld.env.libs_path, "lib22.c"), "2-v2"),
        (os.path.join(bld.env.libs_path, "lib21.c"), "21"),
    ]
    if bld.variant == "docs":
        source = [
            bld.path.find_node("docs/CHANGELOG.rst"),
            bld.path.find_node("docs/api.rst"),
            bld.path.find_node("docs/build/wscript.rst"),
            bld.path.find_node("docs/build.rst"),
            bld.path.find_node("docs/ci.rst"),
            bld.path.find_node("docs/contributing.rst"),
            bld.path.find_node("docs/demos.rst"),
            bld.path.find_node("docs/install.rst"),
            bld.path.find_node("docs/license.rst"),
            bld.path.find_node("docs/manual.rst"),
            bld.path.find_node("docs/sources.rst"),
            bld.path.find_node("docs/start.rst"),
            bld.path.find_node("docs/test.rst"),
            bld.path.find_node("docs/src/lapi.rst"),
            bld.path.find_node("docs/src/lauxlib.rst"),
            bld.path.find_node("docs/src/lbaselib.rst"),
            bld.path.find_node("docs/src/lcode.rst"),
            bld.path.find_node("docs/src/lcorolib.rst"),
            bld.path.find_node("docs/src/lctype.rst"),
            bld.path.find_node("docs/src/ldblib.rst"),
            bld.path.find_node("docs/src/ldebug.rst"),
            bld.path.find_node("docs/src/ldo.rst"),
            bld.path.find_node("docs/src/ldump.rst"),
            bld.path.find_node("docs/src/lfunc.rst"),
            bld.path.find_node("docs/src/lgc.rst"),
            bld.path.find_node("docs/src/linit.rst"),
            bld.path.find_node("docs/src/liolib.rst"),
            bld.path.find_node("docs/src/llex.rst"),
            bld.path.find_node("docs/src/llimits.rst"),
            bld.path.find_node("docs/src/lmathlib.rst"),
            bld.path.find_node("docs/src/lmem.rst"),
            bld.path.find_node("docs/src/loadlib.rst"),
            bld.path.find_node("docs/src/lobject.rst"),
            bld.path.find_node("docs/src/lopcodes.rst"),
            bld.path.find_node("docs/src/loslib.rst"),
            bld.path.find_node("docs/src/lparser.rst"),
            bld.path.find_node("docs/src/lprefix.rst"),
            bld.path.find_node("docs/src/lstate.rst"),
            bld.path.find_node("docs/src/lstring.rst"),
            bld.path.find_node("docs/src/lstrlib.rst"),
            bld.path.find_node("docs/src/ltable.rst"),
            bld.path.find_node("docs/src/ltablib.rst"),
            bld.path.find_node("docs/src/ltm.rst"),
            bld.path.find_node("docs/src/lua.rst"),
            bld.path.find_node("docs/src/luac.rst"),
            bld.path.find_node("docs/src/luaconf.rst"),
            bld.path.find_node("docs/src/lualib.rst"),
            bld.path.find_node("docs/src/lundump.rst"),
            bld.path.find_node("docs/src/lutf8lib.rst"),
            bld.path.find_node("docs/src/lvm.rst"),
            bld.path.find_node("docs/src/lzio.rst"),
            bld.path.find_node("docs/tests/all.rst"),
            bld.path.find_node("docs/tests/api.rst"),
            bld.path.find_node("docs/tests/attrib.rst"),
            bld.path.find_node("docs/tests/big.rst"),
            bld.path.find_node("docs/tests/bitwise.rst"),
            bld.path.find_node("docs/tests/calls.rst"),
            bld.path.find_node("docs/tests/closure.rst"),
            bld.path.find_node("docs/tests/code.rst"),
            bld.path.find_node("docs/tests/constructs.rst"),
            bld.path.find_node("docs/tests/coroutine.rst"),
            bld.path.find_node("docs/tests/db.rst"),
            bld.path.find_node("docs/tests/errors.rst"),
            bld.path.find_node("docs/tests/events.rst"),
            bld.path.find_node("docs/tests/files.rst"),
            bld.path.find_node("docs/tests/gc.rst"),
            bld.path.find_node("docs/tests/goto.rst"),
            bld.path.find_node("docs/tests/libs/lib1.rst"),
            bld.path.find_node("docs/tests/libs/lib11.rst"),
            bld.path.find_node("docs/tests/libs/lib2.rst"),
            bld.path.find_node("docs/tests/libs/lib21.rst"),
            bld.path.find_node("docs/tests/libs.rst"),
            bld.path.find_node("docs/tests/literals.rst"),
            bld.path.find_node("docs/tests/locals.rst"),
            bld.path.find_node("docs/tests/ltests/ltests.rst"),
            bld.path.find_node("docs/tests/ltests.rst"),
            bld.path.find_node("docs/tests/main.rst"),
            bld.path.find_node("docs/tests/math.rst"),
            bld.path.find_node("docs/tests/nextvar.rst"),
            bld.path.find_node("docs/tests/pm.rst"),
            bld.path.find_node("docs/tests/sort.rst"),
            bld.path.find_node("docs/tests/strings.rst"),
            bld.path.find_node("docs/tests/tpack.rst"),
            bld.path.find_node("docs/tests/utf8.rst"),
            bld.path.find_node("docs/tests/vararg.rst"),
            bld.path.find_node("docs/tests/verybig.rst"),
            bld.path.find_node("docs/index.rst"),
        ]
        bld(features="sphinx", source=source, confpy="docs/conf.py", buildername="html")
        bld(features="doxygen", conf="docs/doxygen.conf")
    else:
        if bld.env.generic:
            build_generic(bld)
        elif bld.env.host_os == "aix":
            build_aix(bld)
        elif bld.env.host_os == "openbsd":
            build_openbsd(bld)
        elif bld.env.host_os == "netbsd":
            build_netbsd(bld)
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
            build_solaris(bld)
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
        build_lib_tests(bld, defines_tests)


def build_aix(bld):
    use = ["M", "DL"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_POSIX", "LUA_USE_DLOPEN"]
    defines_tests = []
    cflags = []
    includes = []
    bld.fatal("TODO")


def build_openbsd(bld):
    use = ["M"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_POSIX", "LUA_USE_DLOPEN"]
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

    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        defines=defines,
        cflags=bld.env.CMCFLAGS,
        includes=includes,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests + ["cm_objects"],
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
        build_lib_tests(bld, defines_tests)


def build_netbsd(bld):
    use = ["M"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_POSIX", "LUA_USE_DLOPEN"]
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

    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        defines=defines,
        cflags=bld.env.CMCFLAGS,
        includes=includes,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests + ["cm_objects"],
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
        build_lib_tests(bld, defines_tests)


def build_freebsd(bld):
    use = ["M", "DL", "EDIT"]
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

    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        defines=defines,
        cflags=bld.env.CMCFLAGS,
        includes=includes,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests + ["cm_objects"],
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
        build_lib_tests(bld, defines_tests)


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
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        defines=defines,
        cflags=bld.env.CMCFLAGS,
        includes=includes,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests + ["cm_objects"],
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
        build_lib_tests(bld, defines_tests)


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
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        defines=defines,
        cflags=bld.env.CMCFLAGS,
        includes=includes,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests + ["cm_objects"],
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

    if bld.env.include_tests and 0:
        # https://github.com/swaldhoer/native-lua/issues/44
        build_lib_tests(bld, defines_tests)


def build_win32(bld):
    def build_win32_msvc():
        """Building on win32 with msvc"""
        defines = ["LUA_COMPAT_5_2", "_WIN32"]
        bld(
            features="c",
            source=bld.env.compiler_module_sources,
            target="cm_objects",
            defines=defines,
            cflags=bld.env.CMCFLAGS,
        )
        bld.stlib(
            source=bld.env.sources,
            target="lua",
            defines=defines,
            use=["cm_objects"],
            name="static-lua-library",
        )
        bld.shlib(
            source=bld.env.sources,
            target="luadll",
            defines=defines + ["LUA_BUILD_AS_DLL"],
            use=["cm_objects"],
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

        if bld.env.include_tests:
            pass
            # https://github.com/swaldhoer/native-lua/issues/46

    def build_win32_gcc():
        use = ["M"]
        use_ltests = []
        defines = ["LUA_COMPAT_5_2", "_WIN32"]
        defines_tests = []
        cflags = []
        includes = []

        bld(
            features="c",
            source=bld.env.compiler_module_sources,
            target="cm_objects",
            defines=defines,
            cflags=cflags + bld.env.CMCFLAGS,
            use=use_ltests,
            includes=includes,
        )
        bld.stlib(
            source=bld.env.sources,
            target="lua",
            defines=defines,
            use=["cm_objects"],
            name="static-lua-library",
        )
        bld.shlib(
            source=bld.env.sources,
            target="luadll",
            defines=defines + ["LUA_BUILD_AS_DLL"],
            use=["cm_objects"],
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

        if bld.env.include_tests:
            pass
            # https://github.com/swaldhoer/native-lua/issues/46

    def build_win32_clang():
        use = ["M"]
        use_ltests = []
        defines = ["LUA_COMPAT_5_2", "_WIN32"]
        defines_tests = []
        cflags = []
        includes = []
        bld(
            features="c",
            source=bld.env.compiler_module_sources,
            target="cm_objects",
            defines=defines,
            cflags=cflags + bld.env.CMCFLAGS,
            use=use_ltests,
            includes=includes,
        )
        bld.stlib(
            source=bld.env.sources,
            target="lua",
            defines=defines,
            use=["cm_objects"],
            name="static-lua-library",
        )
        bld.shlib(
            source=bld.env.sources,
            target="luadll",
            defines=defines + ["LUA_BUILD_AS_DLL"],
            use=["cm_objects"],
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

        if bld.env.include_tests and 0:
            # https://github.com/swaldhoer/native-lua/issues/46
            build_lib_tests(bld, defines_tests)

    if bld.env.CC_NAME == "msvc":
        build_win32_msvc()
    elif bld.env.CC_NAME == "gcc":
        build_win32_gcc()
    elif bld.env.CC_NAME == "clang":
        build_win32_clang()


def build_cygwin(bld):
    use = ["M"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_LINUX"]
    defines_tests = []
    cflags = []
    includes = []
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        defines=defines,
        cflags=bld.env.CMCFLAGS,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        use=["cm_objects"],
        name="static-lua-library",
    )
    bld.shlib(
        source=bld.env.sources,
        target="luadll",
        defines=defines + ["LUA_BUILD_AS_DLL"],
        use=["cm_objects"],
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
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        defines=defines,
        cflags=bld.env.CMCFLAGS,
        includes=includes,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        defines=defines,
        cflags=cflags,
        use=use_ltests + ["cm_objects"],
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
        build_lib_tests(bld, defines_tests)


def build_lib_tests(bld, defines_tests):
    bld.path.get_bld().make_node(
        os.path.join(bld.env.tests_basepath, "libs", "P1")
    ).mkdir()
    for src, tgt in bld.env.library_test:
        outfile = os.path.join(bld.env.tests_basepath, "libs", tgt)
        bld.shlib(
            source=src,
            target=outfile,
            defines=defines_tests,
            includes=os.path.abspath(
                os.path.join(bld.path.abspath(), bld.env.src_basepath)
            ),
        )
