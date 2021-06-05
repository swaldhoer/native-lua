#!/usr/bin/env python3
# encoding: utf-8

# SPDX-License-Identifier: MIT

import os
import re

import jsonschema
from waflib import Logs, Utils
from waflib.Build import (
    BuildContext,
    CleanContext,
    InstallContext,
    ListContext,
    StepContext,
    UninstallContext,
)

PLATFORM = Utils.unversioned_sys_platform().lower()

VERSION = "0.6.0-devel"
APPNAME = "lua"

REPO_URL = "https://www.github.com/swaldhoer/native-lua"

LUA_LIBRARY_ST = "static-lua-library"
LUA_LIBRARY_SH = "shared-lua-library"
LUA_LTESTS = "LTESTS"

SRC_BASE_PATH = "src"
SRC = [
    os.path.join(SRC_BASE_PATH, "lapi.c"),
    os.path.join(SRC_BASE_PATH, "ldo.c"),
    os.path.join(SRC_BASE_PATH, "lctype.c"),
    os.path.join(SRC_BASE_PATH, "ldebug.c"),
    os.path.join(SRC_BASE_PATH, "ldump.c"),
    os.path.join(SRC_BASE_PATH, "lfunc.c"),
    os.path.join(SRC_BASE_PATH, "lgc.c"),
    os.path.join(SRC_BASE_PATH, "lmem.c"),
    os.path.join(SRC_BASE_PATH, "lobject.c"),
    os.path.join(SRC_BASE_PATH, "lopcodes.c"),
    os.path.join(SRC_BASE_PATH, "lstate.c"),
    os.path.join(SRC_BASE_PATH, "lstring.c"),
    os.path.join(SRC_BASE_PATH, "ltable.c"),
    os.path.join(SRC_BASE_PATH, "ltm.c"),
    os.path.join(SRC_BASE_PATH, "lundump.c"),
    os.path.join(SRC_BASE_PATH, "lvm.c"),
    os.path.join(SRC_BASE_PATH, "lzio.c"),
    os.path.join(SRC_BASE_PATH, "lauxlib.c"),
    os.path.join(SRC_BASE_PATH, "lbaselib.c"),
    os.path.join(SRC_BASE_PATH, "lcorolib.c"),
    os.path.join(SRC_BASE_PATH, "ldblib.c"),
    os.path.join(SRC_BASE_PATH, "liolib.c"),
    os.path.join(SRC_BASE_PATH, "lmathlib.c"),
    os.path.join(SRC_BASE_PATH, "loslib.c"),
    os.path.join(SRC_BASE_PATH, "lstrlib.c"),
    os.path.join(SRC_BASE_PATH, "ltablib.c"),
    os.path.join(SRC_BASE_PATH, "lutf8lib.c"),
    os.path.join(SRC_BASE_PATH, "loadlib.c"),
    os.path.join(SRC_BASE_PATH, "linit.c"),
]
SRC_CM = [
    os.path.join(SRC_BASE_PATH, "lcode.c"),
    os.path.join(SRC_BASE_PATH, "llex.c"),
    os.path.join(SRC_BASE_PATH, "lparser.c"),
]
SRC_INTR = os.path.join(SRC_BASE_PATH, "lua.c")
SRC_COMP = os.path.join(SRC_BASE_PATH, "luac.c")

TESTS_BASE_PATH = "tests"
LTESTS_DIR = os.path.join(TESTS_BASE_PATH, "ltests")
LTESTS_SRC = os.path.join(LTESTS_DIR, "ltests.c")
TEST_FILES = [
    os.path.join(TESTS_BASE_PATH, "all.lua"),
    os.path.join(TESTS_BASE_PATH, "api.lua"),
    os.path.join(TESTS_BASE_PATH, "attrib.lua"),
    os.path.join(TESTS_BASE_PATH, "big.lua"),
    os.path.join(TESTS_BASE_PATH, "bitwise.lua"),
    os.path.join(TESTS_BASE_PATH, "bwcoercion.lua"),
    os.path.join(TESTS_BASE_PATH, "calls.lua"),
    os.path.join(TESTS_BASE_PATH, "closure.lua"),
    os.path.join(TESTS_BASE_PATH, "code.lua"),
    os.path.join(TESTS_BASE_PATH, "constructs.lua"),
    os.path.join(TESTS_BASE_PATH, "coroutine.lua"),
    os.path.join(TESTS_BASE_PATH, "cstack.lua"),
    os.path.join(TESTS_BASE_PATH, "db.lua"),
    os.path.join(TESTS_BASE_PATH, "errors.lua"),
    os.path.join(TESTS_BASE_PATH, "events.lua"),
    os.path.join(TESTS_BASE_PATH, "files.lua"),
    os.path.join(TESTS_BASE_PATH, "gc.lua"),
    os.path.join(TESTS_BASE_PATH, "gengc.lua"),
    os.path.join(TESTS_BASE_PATH, "goto.lua"),
    os.path.join(TESTS_BASE_PATH, "heavy.lua"),
    os.path.join(TESTS_BASE_PATH, "literals.lua"),
    os.path.join(TESTS_BASE_PATH, "locals.lua"),
    os.path.join(TESTS_BASE_PATH, "main.lua"),
    os.path.join(TESTS_BASE_PATH, "math.lua"),
    os.path.join(TESTS_BASE_PATH, "nextvar.lua"),
    os.path.join(TESTS_BASE_PATH, "pm.lua"),
    os.path.join(TESTS_BASE_PATH, "sort.lua"),
    os.path.join(TESTS_BASE_PATH, "strings.lua"),
    os.path.join(TESTS_BASE_PATH, "tpack.lua"),
    os.path.join(TESTS_BASE_PATH, "utf8.lua"),
    os.path.join(TESTS_BASE_PATH, "vararg.lua"),
    os.path.join(TESTS_BASE_PATH, "verybig.lua"),
]
TEST_LIBS_DIR = os.path.join(TESTS_BASE_PATH, "libs")

INC_FILES = [
    os.path.join(SRC_BASE_PATH, "lua.h"),
    os.path.join(SRC_BASE_PATH, "luaconf.h"),
    os.path.join(SRC_BASE_PATH, "lualib.h"),
    os.path.join(SRC_BASE_PATH, "lauxlib.h"),
    os.path.join(SRC_BASE_PATH, "lua.hpp"),
]

MAN_FILES = [
    os.path.join("docs", "_static", "doc", "lua.1"),
    os.path.join("docs", "_static", "doc", "luac.1"),
]


def validate_json_schema(data: dict, schema=dict) -> bool:
    valid = False
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError:
        pass
    else:
        valid = True
    return valid


for x in ["bin", "docs"]:
    if x == "bin":
        for y in (
            BuildContext,
            CleanContext,
            ListContext,
            StepContext,
            InstallContext,
            UninstallContext,
        ):
            NAME = y.__name__.replace("Context", "").lower()

            class Tmp2(y):
                __doc__ = y.__doc__ + f" ({x})"
                cmd = NAME
                variant = x

    if x == "docs":
        for y in (BuildContext, CleanContext):
            NAME = y.__name__.replace("Context", "").lower()

            class Tmp1(y):
                __doc__ = y.__doc__ + f" ({x})"
                cmd = NAME + "-" + x
                variant = x


if PLATFORM == "win32":
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
        dest="c_std",
        help=(
            "Overwrite default C standard, e.g., '-std=gnu99' for gcc. "
            "This option can only be set during configuration.",
        ),
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
        help="Build with a generic setup for host platform.",
    )


def configure(conf):  # pylint: disable=too-many-branches,too-many-locals
    """Basic configuration of the project based on the operating system and
    the available compilers.
    """
    conf.env.VERSION = VERSION
    conf.env.APPNAME = APPNAME
    conf.msg("Project", f"{conf.env.APPNAME}-{conf.env.VERSION}")
    conf.load("python")
    conf.check_python_version((3, 6))
    conf.undefine("PYTHONDIR")
    conf.undefine("PYTHONARCHDIR")

    base_err_msg = (
        "wscript's VERSION attribute ({}) and version information in file {} "
        "({}) do not match."
    )

    version_file = conf.path.find_node("VERSION")
    version_info = version_file.read_json()
    version_file_ver = version_info["native Lua"]
    if not VERSION == version_file_ver:
        conf.fatal(base_err_msg.format(VERSION, version_file, version_file_ver))

    confpy_file = conf.path.find_node(os.path.join("docs", "conf.py"))
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

    start_file = conf.path.find_node(os.path.join("docs", "start.rst"))
    start_txt = start_file.read(encoding="utf-8")
    start_file_ver = re.search(r"(based on native Lua )\((.{0,})\)", start_txt).group(2)
    if not VERSION == readme_file_ver:
        conf.fatal(base_err_msg.format(VERSION, start_file, start_file_ver))

    doxygen_file = conf.path.find_node(os.path.join("docs", "doxygen.conf"))
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
    conf.env.generic = conf.options.generic
    conf.msg("Platform", conf.options.generic or PLATFORM)
    conf.load("gnu_dirs")

    conf.env.WAF_CONFIG_H_PRELUDE = (
        conf.path.find_node(os.path.join("cfg", "prelude.h.template"))
        .read()
        .replace("{{ VERSION }}", VERSION)
        .replace("{{ REPO_URL }}", REPO_URL)
    )
    conf.write_config_header(configfile="waf_build_config.h")
    platform_configs = conf.path.find_node(
        os.path.join("cfg", "platforms.json")
    ).read_json()
    is_known = platform_configs["known-platforms"].get(PLATFORM, False)
    if not is_known:
        pass  # TODO
    if conf.options.generic:
        pass  # TODO

    schema_compiler_setup = conf.path.find_node(
        os.path.join("cfg", "compiler-cfg.schema.json")
    ).read_json()
    cfgs = conf.path.ant_glob(
        "cfg/**/*.json",
        excl=["**/*.schema.json", "cfg/generic.json", "cfg/platforms.json"],
    )
    Logs.debug(", ".join(i.relpath() for i in cfgs))
    for i in cfgs:
        valid = validate_json_schema(i.read_json(), schema_compiler_setup)
        if not valid:
            Logs.warn(f"{i.relpath()} is not a valid compiler setup.")
    generic_build = conf.path.find_node(os.path.join("cfg", "generic.json")).read_json()
    for _, v in generic_build.items():
        validate_json_schema(v, schema_compiler_setup)

    conf.load("compiler_c")
    if Utils.is_win32 and conf.env.CC_NAME.lower() == "msvc":
        # make msvc include paths absolute
        conf.load("msvc_patch", tooldir="scripts")

    # load platform-compiler configuration
    cc_config_file = os.path.join(
        "cfg", PLATFORM, f"{PLATFORM}_{conf.env.CC_NAME}.json"
    )
    cc_config = conf.path.find_node(cc_config_file).read_json()
    for i, val in cc_config.items():
        if i.isupper() or "_PATTERN" in i:
            conf.env[i] = val
    # add the build directory to includes as it stores the configuration file
    conf.env.append_unique("INCLUDES", [conf.path.get_bld().abspath()])

    # validate C standard setting
    conf.env.C_STD = cc_config["std"]["opt"] + cc_config["std"]["val"]
    if conf.options.c_std:  # setting might be overwritten on commandline
        conf.env.C_STD = conf.options.c_std
    conf.env.append_unique("CFLAGS", [conf.env.C_STD])
    if "89" in conf.env.C_STD:
        if PLATFORM == "win32" and conf.env.CC_NAME.lower() == "msvc":
            Logs.warn("This will NOT effect msvc-builds on win32.")
        else:
            Logs.warn(
                "C89 does not guarantee 64-bit integers for Lua.Adding define: LUA_USE_C89"
            )
            Logs.warn("Adding define: LUA_USE_C89")
            conf.define("LUA_USE_C89", 1)  # TODO check for waf update

    min_c = "#include<stdio.h>\nint main() {\n    return 0;\n}\n"

    lib_tests = []
    for lib in cc_config.get("libs", []):
        lib_tests.append(
            {
                "lib": lib,
                "uselib_store": lib.upper(),
                "msg": f"Checking for library '{lib}'",
            }
        )

    conf.multicheck(
        {"fragment": min_c, "execute": True, "msg": "Minimal C program"},
        {
            "fragment": min_c,
            "execute": True,
            "cflags": conf.env.C_STD,
            "msg": f"Checking c-standard '{conf.env.C_STD}'",
        },
        *lib_tests,
        {
            "fragment": min_c,
            "execute": True,
            "cflags": conf.env.C_STD,
            "use": [i.upper() for i in cc_config.get("libs", [])],
            "msg": "Checking for all libraries",
        },
        msg="Validating compiler setup",
        mandatory=True,
        run_all_tests=True,
    )
    if cc_config.get("libs", []):
        conf.env.USE_LIBS = [i.upper() for i in cc_config["libs"]]
    # doc tools
    conf.load("sphinx", tooldir="scripts")
    conf.load("doxygen", tooldir="scripts")

    # check that the version number follows semantic versioning
    conf.load("semver", tooldir="scripts")


def build(bld):
    """Wrapper for the compiler specific build"""
    if bld.variant == "docs":
        bld(recurse="docs")
        return
    # check that the binary will be available in PATH
    if bld.cmd.startswith("install"):
        bin_dir = Utils.subst_vars(bld.env.BINDIR, bld.env)
        paths = os.environ["PATH"].split(os.pathsep)
        if not any(x if x == bin_dir else False for x in paths):
            Logs.warn(f"lua is not in available in PATH (add {bin_dir}).")

    # setup install files
    for i in INC_FILES:
        bld.install_files("${INCLUDEDIR}", bld.path.find_node(i))
    if Utils.is_win32:
        if bld.env.CC_NAME == "gcc":
            pass  # the DLL produced by gcc is already installed to ${BINDIR}
        if bld.env.CC_NAME == "msvc":
            bininst = bld.path.get_bld().ant_glob("*.dll **/*.manifest", quiet=True)
            libinst = []
            if bld.env.MSVC_MANIFEST:
                bininst += bld.path.get_bld().ant_glob("**/*.manifest", quiet=True)
                libinst += bld.path.get_bld().ant_glob("**/*dll.manifest", quiet=True)
            bld.install_files("${BINDIR}", bininst)
            bld.install_files("${LIBDIR}", libinst)
    else:  # man files do not make sense on win32
        for i in MAN_FILES:
            bld.install_files("${MANDIR}/man1", bld.path.find_node(i))

    # application build
    bld.env.append_unique("INCLUDES", SRC_BASE_PATH)
    if bld.options.ltests:
        if bld.env.CC_NAME.lower() == "msvc":
            bld.env.append_unique("CFLAGS", ["/Zi", "/FS"])
        else:  # all other compilers should understand -g
            bld.env.append_unique("CFLAGS", "-g")
        bld.define("LUA_USER_H", "ltests.h", quote=True)
        bld.env.append_unique("INCLUDES", LTESTS_DIR)
    library_tests = [
        (os.path.join(TEST_LIBS_DIR, "lib1.c"), "1"),
        (os.path.join(TEST_LIBS_DIR, "lib11.c"), "11"),
        (os.path.join(TEST_LIBS_DIR, "lib2.c"), "2"),
        (os.path.join(TEST_LIBS_DIR, "lib22.c"), "2-v2"),
        (os.path.join(TEST_LIBS_DIR, "lib21.c"), "21"),
    ]

    if bld.options.include_tests:
        bld(features="subst", source=TEST_FILES, target=TEST_FILES, is_copy=True)
        bld.path.find_or_declare(os.path.join(TEST_LIBS_DIR, "P1")).mkdir()

        if PLATFORM not in ["cygwin", "darwin", "win32"]:
            for src, tgt in library_tests:
                outfile = os.path.join(TESTS_BASE_PATH, "libs", tgt)
                bld.shlib(source=src, target=outfile, includes=SRC_BASE_PATH)

    if bld.options.ltests:
        bld.objects(source=LTESTS_SRC, name=LUA_LTESTS)

    if bld.options.generic:
        bld.fatal("TODO")

    bld.objects(source=SRC_CM, cflags=bld.env.CMCFLAGS, target="cm")
    bld.stlib(source=SRC, target="lua", use=["cm", LUA_LTESTS], name=LUA_LIBRARY_ST)
    use = [LUA_LIBRARY_ST] + bld.env.USE_LIBS
    bld.program(source=SRC_COMP, target="luac", use=use)
    if PLATFORM in ["cygwin", "win32"]:
        bld.shlib(
            source=SRC,
            target="luadll",
            defines="LUA_BUILD_AS_DLL",
            use=["cm", LUA_LTESTS],
            name=LUA_LIBRARY_SH,
        )
        use_intr = [LUA_LIBRARY_SH] + bld.env.USE_LIBS
        bld.program(source=SRC_INTR, target="lua", use=use_intr)
    elif PLATFORM in [
        "aix",
        "darwin",
        "netbsd",
        "openbsd",
        "freebsd",
        "linux",
        "solaris",
    ]:
        bld.program(source=SRC_INTR, target="lua", use=use)
    else:
        bld.fatal("Platform currently not supported. Try the generic build option.")
