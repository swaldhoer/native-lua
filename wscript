#!/usr/bin/env python3
# encoding: utf-8

# SPDX-License-Identifier: MIT

# pylint: disable=unused-variable

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

VERSION = "0.6.0-devel"
APPNAME = "lua"
top = "."  # pylint: disable=invalid-name
out = "build"  # pylint: disable=invalid-name


REPO_URL = "https://www.github.com/swaldhoer/native-lua"


def validate_json_schema(data: dict, schema=dict) -> bool:
    valid = False
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
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


if Utils.unversioned_sys_platform().lower() == "win32":
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
        help="Overwrite default C standard, e.g., '-std=gnu99' for gcc.",
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
        help="Build generic setup for host platform.",
    )


def configure(conf):  # pylint: disable=too-many-branches,too-many-locals
    """Basic configuration of the project based on the operating system and
    the available compilers.
    """
    plat = Utils.unversioned_sys_platform().lower()
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
        conf.fatal(base_err_msg.format(VERSION, readme_file, readme_file_ver))

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

    min_c = "#include<stdio.h>\nint main() {\n    return 0;\n}\n"

    if conf.options.c_standard == "c89":
        if Utils.unversioned_sys_platform().lower() == "win32":
            Logs.warn("This will NOT effect msvc-builds on win32.")
        else:
            Logs.warn("C89 does not guarantee 64-bit integers for Lua.")
            Logs.warn("Adding define: LUA_USE_C89")  # TODO

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
    for k, v in generic_build.items():
        validate_json_schema(v, schema_compiler_setup)

    conf.load("compiler_c")
    if Utils.is_win32 and conf.env.CC_NAME.lower() == "msvc":
        # make msvc include paths absolute
        conf.load("msvc_patch", tooldir="scripts")

    # load platform-compiler configuration
    cc_config_file = os.path.join("cfg", plat, f"{plat}_{conf.env.CC_NAME}.json")
    cc_config = conf.path.find_node(cc_config_file).read_json()
    for i, val in cc_config.items():
        if not val:  # if a setting is empty do not overwrite default values
            continue
        if i.isupper() or "_PATTERN" in i:
            conf.env[i] = val
    # add the build directory to includes as it stores the configuration file
    conf.env.append_unique("INCLUDES", [conf.path.get_bld().abspath()])

    # validate C standard setting
    c_std = cc_config["std"]["opt"] + cc_config["std"]["val"]
    msg = f'Checking c-standard \'{cc_config["std"]["val"]}\''
    conf.check_cc(fragment=min_c, execute=True, cflags=c_std, msg=msg)
    conf.env.append_unique("CFLAGS", [c_std])
    conf.check_cc(fragment=min_c, execute=True)
    # check for libraries
    for lib in cc_config.get("libs", []):
        conf.check(lib=lib, uselib_store=lib.upper())
    # check all libraries
    test_use = [i.upper() for i in cc_config.get("libs", [])]
    msg = "Checking for all libraries"
    conf.check_cc(fragment=min_c, use=test_use, execute=True, cflags=c_std, msg=msg)

    # doc tools
    conf.load("sphinx", tooldir="scripts")
    conf.load("doxygen", tooldir="scripts")

    # check that the version number follows semantic versioning
    conf.load("semver", tooldir="scripts")


def build(bld):
    """Wrapper for the compiler specific build"""
    if bld.variant == "docs":
        source = [
            bld.path.find_node("docs/changelog.rst"),
            bld.path.find_node("docs/api.rst"),
            bld.path.find_node("docs/build.rst"),
            bld.path.find_node("docs/ci.rst"),
            bld.path.find_node("docs/contributing.rst"),
            bld.path.find_node("docs/demos.rst"),
            bld.path.find_node("docs/install.rst"),
            bld.path.find_node("docs/license.rst"),
            bld.path.find_node("docs/manual.rst"),
            bld.path.find_node("docs/start.rst"),
            bld.path.find_node("docs/test.rst"),
            bld.path.find_node("docs/index.rst"),
        ]
        bld(features="sphinx", source=source, confpy="docs/conf.py", buildername="html")
        bld(features="doxygen", conf="docs/doxygen.conf")
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

    if bld.options.generic:
        build_generic(bld)
    elif Utils.unversioned_sys_platform().lower() == "aix":
        build_aix(bld)
    elif Utils.unversioned_sys_platform().lower() == "cygwin":
        build_cygwin(bld)
    elif Utils.unversioned_sys_platform().lower() == "darwin":
        build_darwin(bld)
    elif Utils.unversioned_sys_platform().lower() == "freebsd":
        build_freebsd(bld)
    elif Utils.unversioned_sys_platform().lower() == "linux":
        build_linux(bld)
    elif Utils.unversioned_sys_platform().lower() == "netbsd":
        build_netbsd(bld)
    elif Utils.unversioned_sys_platform().lower() == "openbsd":
        build_openbsd(bld)
    elif Utils.unversioned_sys_platform().lower() == "solaris":
        build_solaris(bld)
    elif Utils.unversioned_sys_platform().lower() == "win32":
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
    use = ["M"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2"]
    defines_tests = []
    cflags = []
    includes = []
    if bld.options.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.options.ltests:
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

    if bld.options.include_tests:
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
    if bld.options.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.options.ltests:
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

    if bld.options.include_tests:
        build_lib_tests(bld, defines_tests)


def build_netbsd(bld):
    use = ["M"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_POSIX", "LUA_USE_DLOPEN"]
    defines_tests = []
    cflags = []
    includes = []
    if bld.options.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.options.ltests:
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

    if bld.options.include_tests:
        build_lib_tests(bld, defines_tests)


def build_freebsd(bld):
    use = ["M", "DL", "EDIT"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_LINUX"]
    defines_tests = []
    cflags = []
    includes = []
    if bld.options.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.options.ltests:
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

    if bld.options.include_tests:
        build_lib_tests(bld, defines_tests)


def build_linux(bld):
    use = ["M", "DL", "READLINE"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_LINUX"]
    defines_tests = []
    cflags = []
    includes = []
    if bld.options.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.options.ltests:
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

    if bld.options.include_tests:
        build_lib_tests(bld, defines_tests)


def build_darwin(bld):
    use = ["M", "READLINE"]
    use_ltests = []
    defines = ["LUA_COMPAT_5_2", "LUA_USE_MACOSX"]
    defines_tests = []
    cflags = []
    includes = []
    if bld.options.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.options.ltests:
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

    if bld.options.include_tests:  # https://github.com/swaldhoer/native-lua/issues/44
        pass  # build_lib_tests(bld, defines_tests)


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

        if bld.options.include_tests:
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

        if bld.options.include_tests:
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

        if bld.options.include_tests:
            # https://github.com/swaldhoer/native-lua/issues/46
            pass  # build_lib_tests(bld, defines_tests)

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
    if bld.options.c_standard.endswith("89"):
        defines_c89 = ["LUA_USE_C89"]
        defines_tests += defines_c89
        defines += defines_c89
    if bld.options.ltests:
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

    if bld.options.include_tests:
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
