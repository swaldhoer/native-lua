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

from waflib.Utils import unversioned_sys_platform as usp

VERSION = "0.6.0-devel"
APPNAME = "lua"

REPO_URL = "https://www.github.com/swaldhoer/native-lua"

LUA_LIBRARY_ST = "static-lua-library"
LUA_LIBRARY_SH = "shared-lua-library"


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


if usp().lower() == "win32":
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
    plat = usp().lower()
    conf.env.VERSION = VERSION
    conf.env.APPNAME = APPNAME
    conf.msg("Project", f"{conf.env.APPNAME}-{conf.env.VERSION}")
    conf.load("python")
    conf.check_python_version((3, 6))
    conf.env.define_key.remove("PYTHONDIR")
    conf.env.define_key.remove("PYTHONARCHDIR")

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
    conf.msg("Platform", conf.options.generic or plat)
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
    is_known = platform_configs["known-platforms"].get(plat, False)
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
    cc_config_file = os.path.join("cfg", plat, f"{plat}_{conf.env.CC_NAME}.json")
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
        if usp().lower() == "win32" and conf.env.CC_NAME.lower() == "msvc":
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
    # check that the binary is available in PATH
    if bld.cmd.startswith("install"):
        bin_dir = Utils.subst_vars(bld.env.BINDIR, bld.env)
        if not any(
            x if x == bin_dir else False for x in os.environ["PATH"].split(os.pathsep)
        ):
            Logs.warn("lua is not in available in PATH.")
            Logs.warn("Add the following path to PATH: {}".format(bin_dir))

    # setup install files
    if Utils.is_win32:
        if bld.env.CC_NAME == "gcc":
            # the DLL produced by gcc is already installed to ${BINDIR}
            pass
        if bld.env.CC_NAME == "msvc":
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

    incfiles = [
        bld.path.find_node(os.path.join("src", "lua.h")),
        bld.path.find_node(os.path.join("src", "luaconf.h")),
        bld.path.find_node(os.path.join("src", "lualib.h")),
        bld.path.find_node(os.path.join("src", "lauxlib.h")),
        bld.path.find_node(os.path.join("src", "lua.hpp")),
    ]
    bld.install_files("${INCLUDEDIR}", incfiles)

    # application build
    bld.env.src_basepath = "src"
    bld.env.append_unique("INCLUDES", bld.env.src_basepath)
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
    if bld.options.ltests:
        if bld.env.CC_NAME.lower() == "msvc":
            bld.env.append_unique("CFLAGS", ["/Zi", "/FS"])
        else:
            bld.env.append_unique("CFLAGS", "-g")
        bld.define("LUA_USER_H", "ltests.h", quote=True)
        bld.env.append_unique("INCLUDES", bld.env.ltests_dir)
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

    if bld.options.generic:
        build_generic(bld)
    elif usp().lower() == "aix":
        build_aix(bld)
    elif usp().lower() == "cygwin":
        build_cygwin(bld)
    elif usp().lower() == "darwin":
        build_darwin(bld)
    elif usp().lower() == "freebsd":
        build_freebsd(bld)
    elif usp().lower() == "linux":
        build_linux(bld)
    elif usp().lower() == "netbsd":
        build_netbsd(bld)
    elif usp().lower() == "openbsd":
        build_openbsd(bld)
    elif usp().lower() == "solaris":
        build_solaris(bld)
    elif usp().lower() == "win32":
        build_win32(bld)
    else:
        bld.fatal("currently not supported platform.")

    if bld.options.include_tests:
        bld(
            features="subst",
            source=bld.env.test_files,
            target=bld.env.test_files,
            is_copy=True,
        )


def build_generic(bld):
    use_ltests = []
    if bld.options.ltests:
        use_ltests += ["LTESTS"]
        bld.objects(source=bld.env.ltests_sources, name="LTESTS")

    bld.stlib(source=bld.env.sources, target="lua", use=use_ltests, name=LUA_LIBRARY_ST)
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )

    if bld.options.include_tests:
        build_lib_tests(bld)


def build_aix(bld):
    bld.fatal("TODO")


def build_openbsd(bld):
    use_ltests = []
    if bld.options.ltests:
        use_ltests += ["LTESTS"]
        bld.objects(source=bld.env.ltests_sources, name="LTESTS")
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        cflags=bld.env.CMCFLAGS,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        use=use_ltests + ["cm_objects"],
        name=LUA_LIBRARY_ST,
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )

    if bld.options.include_tests:
        build_lib_tests(bld)


def build_netbsd(bld):
    use_ltests = []
    if bld.options.ltests:
        use_ltests += ["LTESTS"]
        bld.objects(source=bld.env.ltests_sources, name="LTESTS")
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        cflags=bld.env.CMCFLAGS,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        use=use_ltests + ["cm_objects"],
        name=LUA_LIBRARY_ST,
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )

    if bld.options.include_tests:
        build_lib_tests(bld)


def build_freebsd(bld):
    use_ltests = []
    if bld.options.ltests:
        use_ltests += ["LTESTS"]
        bld.objects(source=bld.env.ltests_sources, name="LTESTS")
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        cflags=bld.env.CMCFLAGS,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        use=use_ltests + ["cm_objects"],
        name=LUA_LIBRARY_ST,
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )

    if bld.options.include_tests:
        build_lib_tests(bld)


def build_linux(bld):
    use_ltests = []
    if bld.options.ltests:
        use_ltests += ["LTESTS"]
        bld.objects(source=bld.env.ltests_sources, name="LTESTS")
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        cflags=bld.env.CMCFLAGS,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        use=use_ltests + ["cm_objects"],
        name=LUA_LIBRARY_ST,
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )

    if bld.options.include_tests:
        build_lib_tests(bld)


def build_darwin(bld):
    use_ltests = []
    if bld.options.ltests:
        use_ltests += ["LTESTS"]
        bld.objects(source=bld.env.ltests_sources, name="LTESTS")
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        cflags=bld.env.CMCFLAGS,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        use=use_ltests + ["cm_objects"],
        name=LUA_LIBRARY_ST,
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )

    if bld.options.include_tests:  # https://github.com/swaldhoer/native-lua/issues/44
        pass  # build_lib_tests(bld)


def build_win32(bld):
    def build_win32_msvc():
        """Building on win32 with msvc"""
        use_ltests = []
        if bld.options.ltests:
            use_ltests += ["LTESTS"]
            bld.objects(source=bld.env.ltests_sources, target="LTESTS")
        bld.objects(
            source=bld.env.compiler_module_sources,
            target="cm_objects",
            cflags=bld.env.CMCFLAGS,
        )
        bld.stlib(
            source=bld.env.sources,
            target="lua",
            use=["cm_objects"] + use_ltests,
            name=LUA_LIBRARY_ST,
        )
        bld.shlib(
            source=bld.env.sources,
            target="luadll",
            defines=["LUA_BUILD_AS_DLL"],
            use=["cm_objects"] + use_ltests,
            name=LUA_LIBRARY_SH,
        )
        bld.program(
            source=bld.env.source_interpreter,
            target="lua",
            use=[LUA_LIBRARY_SH] + use_ltests,
        )
        bld.program(
            source=bld.env.source_compiler,
            target="luac",
            use=[LUA_LIBRARY_ST] + use_ltests,
        )

        if bld.options.include_tests:
            pass
            # https://github.com/swaldhoer/native-lua/issues/46

    def build_win32_gcc():
        use_ltests = []
        if bld.options.ltests:
            use_ltests += ["LTESTS"]
            bld.objects(source=bld.env.ltests_sources, name="LTESTS")
        bld.objects(
            source=bld.env.compiler_module_sources,
            target="cm_objects",
            cflags=bld.env.CMCFLAGS,
        )
        bld.stlib(
            source=bld.env.sources,
            target="lua",
            use=use_ltests + ["cm_objects"],
            name=LUA_LIBRARY_ST,
        )
        bld.shlib(
            source=bld.env.sources,
            target="luadll",
            defines=["LUA_BUILD_AS_DLL"],
            use=use_ltests + ["cm_objects"],
            name=LUA_LIBRARY_SH,
        )
        bld.program(
            source=bld.env.source_interpreter,
            target="lua",
            use=[LUA_LIBRARY_SH] + bld.env.USE_LIBS + use_ltests,
        )
        bld.program(
            source=bld.env.source_compiler,
            target="luac",
            use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
        )

        if bld.options.include_tests:
            pass
            # https://github.com/swaldhoer/native-lua/issues/46

    def build_win32_clang():
        use_ltests = []
        if bld.options.ltests:
            use_ltests += ["ltests"]
            bld(features="c", source=bld.env.ltests_sources, name="ltests", target="ltests")
        bld.objects(
            source=bld.env.compiler_module_sources,
            target="cm_objects",
            cflags=bld.env.CMCFLAGS,
        )
        bld.stlib(
            source=bld.env.sources,
            target="lua",
            use=["cm_objects"] + use_ltests,
            name=LUA_LIBRARY_ST,
        )
        bld.shlib(
            source=bld.env.sources,
            target="luadll",
            defines=["LUA_BUILD_AS_DLL"],
            use=["cm_objects"] + use_ltests,
            name=LUA_LIBRARY_SH,
        )
        bld.program(
            source=bld.env.source_interpreter,
            target="lua",
            use=[LUA_LIBRARY_SH] + bld.env.USE_LIBS+ ["ltests"],
        )
        bld.program(
            source=bld.env.source_compiler,
            target="luac",
            use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS,
        )

        if bld.options.include_tests:
            # https://github.com/swaldhoer/native-lua/issues/46
            pass  # build_lib_tests(bld)

    if bld.env.CC_NAME == "msvc":
        build_win32_msvc()
    elif bld.env.CC_NAME == "gcc":
        build_win32_gcc()
    elif bld.env.CC_NAME == "clang":
        build_win32_clang()


def build_cygwin(bld):
    use_ltests = []
    if bld.options.ltests:
        use_ltests += ["LTESTS"]
        bld.objects(source=bld.env.ltests_sources, name="LTESTS")
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        cflags=bld.env.CMCFLAGS,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        use=["cm_objects"],
        name=LUA_LIBRARY_ST,
    )
    bld.shlib(
        source=bld.env.sources,
        target="luadll",
        defines=["LUA_BUILD_AS_DLL"],
        use=["cm_objects"],
        name=LUA_LIBRARY_SH,
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        use=[LUA_LIBRARY_SH] + bld.env.USE_LIBS + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )


def build_solaris(bld):
    use_ltests = []
    if bld.options.ltests:
        use_ltests += ["LTESTS"]
        bld.objects(source=bld.env.ltests_sources, name="LTESTS")
    bld.objects(
        source=bld.env.compiler_module_sources,
        target="cm_objects",
        cflags=bld.env.CMCFLAGS,
    )
    bld.stlib(
        source=bld.env.sources,
        target="lua",
        use=use_ltests + ["cm_objects"],
        name=LUA_LIBRARY_ST,
    )
    bld.program(
        source=bld.env.source_interpreter,
        target="lua",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )
    bld.program(
        source=bld.env.source_compiler,
        target="luac",
        use=[LUA_LIBRARY_ST] + bld.env.USE_LIBS + use_ltests,
    )

    if bld.options.include_tests:
        build_lib_tests(bld)


def build_lib_tests(bld):
    bld.path.get_bld().make_node(
        os.path.join(bld.env.tests_basepath, "libs", "P1")
    ).mkdir()
    for src, tgt in bld.env.library_test:
        outfile = os.path.join(bld.env.tests_basepath, "libs", tgt)
        bld.shlib(
            source=src,
            target=outfile,
            includes=os.path.abspath(
                os.path.join(bld.path.abspath(), bld.env.src_basepath)
            ),
        )
