#!/usr/bin/env python
# encoding: utf-8

# SPDX-License-Identifier: MIT

# pylint: disable=unused-variable

import os
import re
import yaml

from waflib import Logs, Utils, Options, Context, Task
from waflib.Tools.compiler_c import c_compiler
from waflib.Tools.c import c  # pylint: disable=W0611
from waflib.Tools import c_preproc
from waflib.Build import BuildContext, CleanContext, ListContext, StepContext
from waflib.Build import InstallContext, UninstallContext


VERSION = "0.2.1"
APPNAME = "lua"
top = "."  # pylint: disable=C0103
out = "build"  # pylint: disable=C0103

Context.Context.line_just = 45


# we overwrite c class, as absolute paths can be parsed by VS Code error parser
class c(Task.Task):  # pylint: disable=C0103,E0102
    run_str = (
        "${CC} ${ARCH_ST:ARCH} ${CFLAGS} ${FRAMEWORKPATH_ST:FRAMEWORKPATH} "
        "${CPPPATH_ST:INCPATHS} ${DEFINES_ST:DEFINES} "
        "${CC_SRC_F}${SRC[0].abspath()} ${CC_TGT_F}${TGT[0].abspath()} "
        "${CPPFLAGS}"
    )
    vars = ["CCDEPS"]
    ext_in = [".h"]
    scan = c_preproc.scan


host_os = Utils.unversioned_sys_platform()  # pylint: disable=C0103

plat_comp = c_compiler["default"]  # pylint: disable=C0103
if c_compiler.get(host_os):
    plat_comp = c_compiler[host_os]  # pylint: disable=C0103
else:
    # add host compilers to compiler list. We need to do this, in order that we
    # use c_compiler[host_os] everywhere we need it.
    c_compiler[host_os] = plat_comp

for x in plat_comp + ["docs"]:
    for y in (BuildContext, CleanContext):
        name = y.__name__.replace("Context", "").lower()

        class Tmp1(y):
            __doc__ = y.__doc__ + " ({})".format(x)
            cmd = name + "_" + x
            variant = x

    if x != "docs":
        for y in (ListContext, StepContext, InstallContext, UninstallContext):
            name = y.__name__.replace("Context", "").lower()

            class Tmp2(y):
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
        help="Build generic on the host " "platform. This is not supported on win32.",
    )


def configure(cnf):  # pylint: disable=R0912
    """Basic configuration of the project based on the operating system and
    the available compilers.
    """
    cnf.msg("Prefix", cnf.env.PREFIX)
    print("-" * (Context.Context.line_just + 1) + ":")
    cnf.load("python")
    cnf.check_python_version((3, 5))

    cnf.load("sphinx", tooldir="scripts")
    cnf.load("doxygen", tooldir="scripts")
    if not cnf.env.SPHINX_BUILD:
        Logs.warn("Documentation build will not be available.")
    else:
        cnf.env.docs_out = os.path.join(out, "docs")

    print("-" * (Context.Context.line_just + 1) + ":")

    # check that all version numbers match and the the version number adheres to
    # Semantic Versioning
    sem_ver_re = re.compile(
        r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*"
        r"[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))"
        r"*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    )

    version_info = yaml.load(
        cnf.path.find_node("VERSION").read(), Loader=yaml.SafeLoader
    )
    cnf.env.project_version = version_info["native Lua"]
    err_msg = "wscript VERSION ({}) and VERSION's native Lua attribute ({}) do not match".format(
        VERSION, cnf.env.project_version
    )
    assert cnf.env.project_version == VERSION, err_msg

    confpy_version = cnf.path.find_node("conf.py").read(encoding="utf-8")
    ver = ""
    for i in confpy_version.split("\n"):
        if i.startswith("version"):
            ver = i.split("=")[1].replace('"', "").strip()
            break
    err_msg = "wscript VERSION ({}) and conf.py version ({}) do not match".format(
        VERSION, ver
    )
    assert ver == VERSION, err_msg
    ver = ""

    readme = cnf.path.find_node("README.rst").read()
    ver = readme.find("based on native Lua ({})".format(VERSION))
    err_msg = "wscript VERSION ({}) and README.rst 'lua -v version' ({}) do not match".format(
        VERSION, ver
    )
    assert ver > 0, err_msg

    cnf.env.lua_src_version = version_info["lua"]
    cnf.env.lua_tests_version = version_info["tests"]
    cnf.msg("native Lua version", cnf.env.project_version)
    cnf.msg("Lua version", cnf.env.lua_src_version)
    cnf.msg("Lua tests version", cnf.env.lua_tests_version)
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

    min_c = "#include<stdio.h>\nint main() {\n    return 0;\n}\n"

    if cnf.options.c_standard == "c89":
        Logs.warn("C89 does not guarantee 64-bit integers for Lua.")
        Logs.warn("Adding define: LUA_USE_C89")  # TODO
        if host_os == "win32":
            Logs.warn("This will NOT effect msvc-builds on win32.")
    cnf.msg("C standard", cnf.options.c_standard)

    cnf.env.WAF_CONFIG_H_PRELUDE = (
        '#define NATIVE_LUA_PRE_MSG "based on native Lua"\n'
        '#define NATIVE_LUA_VERSION "{}"\n'.format(VERSION) + ""
        '#define NATIVE_LUA_REPO "https://github.com/swaldhoer/native-lua"\n'
        '#define NATIVE_LUA_MSG " [" NATIVE_LUA_PRE_MSG " (" NATIVE_LUA_VERSION"), " NATIVE_LUA_REPO"]"\n\n'
        "#if defined(_MSC_VER) && defined(_MSC_FULL_VER)\n"
        "#pragma warning(disable: 4242 4820 4668 4710 4711 5045)\n"
        "/* Disable C5045 (see "
        "https://docs.microsoft.com/de-de/cpp/error-messages/compiler-warnings/c5045) */\n"
        "/* we are compiling with /Qspectre */\n"
        "#endif\n"
    )
    platform_compilers = []
    failed_platform_compilers = []
    cnf.write_config_header()
    if cnf.options.generic:
        if host_os == "win32":
            Logs.info("Generic build uses msvc on win32")
            try:  # msvc
                set_new_basic_env("msvc")
                cnf.load("compiler_c")
                cnf.env.CFLAGS = [
                    "/nologo",
                    cnf.env.c_standard,
                    "/O2",
                    "/Wall",
                    "/Qspectre",
                ]
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
            check_libs("m", "dl", "edit")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.env.LINKFLAGS = ["-Wl,-export-dynamic"]
            cnf.check_cc(fragment=min_c, execute=True)
            cnf.env.append_unique("INCLUDES", "/usr/include/edit")
            cnf.env.append_unique("LIBPATH", "/usr/local/lib")
            check_libs("m", "dl", "edit")
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
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "readline")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env("clang")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [cnf.env.c_standard, "-O2", "-Wall", "-Wextra"]
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs("m", "readline")
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == "win32":
        try:  # msvc
            set_new_basic_env("msvc")
            cnf.load("compiler_c")
            cnf.env.CFLAGS = [
                "/nologo",
                cnf.env.c_standard,
                "/O2",
                "/Wall",
                "/Qspectre",
            ]
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
            # these vars fix the luac build
            cnf.env.cstlib_PATTERN = "%s.lib"
            cnf.env.LINKFLAGS = []
            cnf.env.STLIB_MARKER = ""
            cnf.env.SHLIB_MARKER = ""
            # these vars fix the lua build
            cnf.env.IMPLIB_ST = "-IMPLIB:%s"
            cnf.env.implib_PATTERN = "%s.dll"
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
                " ".join("build_" + t_cc for t_cc in c_compiler[host_os])
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
    bld.env.library_test = [
        (os.path.join(bld.env.libs_path, "lib1.c"), "1"),
        (os.path.join(bld.env.libs_path, "lib11.c"), "11"),
        (os.path.join(bld.env.libs_path, "lib2.c"), "2"),
        (os.path.join(bld.env.libs_path, "lib2.c"), "2-v2"),
        (os.path.join(bld.env.libs_path, "lib21.c"), "21"),
    ]
    if bld.variant == "docs":
        source = bld.path.ant_glob("*.rst docs/**/*.rst")
        bld(features="sphinx", source=source, confpy="conf.py", buildername="html")
        bld(features="doxygen", conf="doxygen.conf")
    else:
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
        build_lib_tests(bld, defines_tests)


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

    if bld.env.include_tests and 0:
        # https://github.com/swaldhoer/native-lua/issues/44
        build_lib_tests(bld, defines_tests)


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

        if bld.env.include_tests:
            pass
            # https://github.com/swaldhoer/native-lua/issues/46

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

        if bld.env.include_tests:
            pass
            # https://github.com/swaldhoer/native-lua/issues/46

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
