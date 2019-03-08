#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import logging

from waflib import Logs, Utils, Options
from waflib.Tools.compiler_c import c_compiler
from waflib.Build import BuildContext, CleanContext, ListContext, StepContext
from waflib.Build import InstallContext, UninstallContext

VERSION = '0.0.1'
APPNAME = 'lua'
top = '.'  # pylint: disable=C0103
out = 'build'  # pylint: disable=C0103

host_os = Utils.unversioned_sys_platform()  # pylint: disable=C0103

plat_comp = c_compiler['default']  # pylint: disable=C0103
if c_compiler.get(host_os):
    plat_comp = c_compiler[host_os]  # pylint: disable=C0103

for x in plat_comp:
    for y in (BuildContext, CleanContext, ListContext, StepContext,
              InstallContext, UninstallContext):
        name = y.__name__.replace('Context', '').lower()
        class Tmp(y):
            __doc__ = y.__doc__ + ' ({})'.format(x)
            cmd = name + '_' + x
            variant = x

if host_os == 'win32':
    os.environ['PREFIX'] = os.path.join(os.environ.get('LOCALAPPDATA'),
                                        'Programs',
                                        'lua')

def options(opt):
    opt.parser.remove_option('--top')
    opt.parser.remove_option('--out')
    opt.load('compiler_c')
    opt.load('gnu_dirs')
    opt.parser.remove_option('--oldincludedir')
    opt.parser.remove_option('--dvidir')
    opt.parser.remove_option('--pdfdir')
    opt.parser.remove_option('--infodir')
    opt.parser.remove_option('--psdir')
    opt.parser.remove_option('--localedir')
    opt_gr = opt.get_option_group('Installation directories')
    opt_gr.add_option('--man1dir',
                      action='store',
                      default='${DATAROOTDIR}/man1',
                      help='system manual pages [DATAROOTDIR/man1]',
                      dest='MAN1DIR')
    opt.add_option('--confcache', dest='confcache', default=0,
                   action='count', help='Use a configuration cache')
    opt.add_option('--include-tests', dest='include_tests', default=False,
                   action='store_true', help='Include test files')
    opt.add_option(
        '--c-std',
        dest='c_standard',
        default='c99',
        choices=['c89', 'c99'],
        help='Specify C-standard to be used. \'c99\' is default. \'c99\' will '
             'be replaced by \'gnu99\' for gcc, xlc and icc. \'c99\' will be '
             'replaced by \'c++14\' for msvc. \'c89\' is passed verbatim for '
             'gcc, xlc, icc and clang. \'c89\' will be replaced by \'c++14\' '
             ' for msvc.')
    opt.add_option('--ltests', dest='ltests', default=False,
                   action='store_true', help='Building with \'ltests\'')
    opt.add_option('--generic', dest='generic', default=False,
                   action='store_true', help='Build generic on the host '
                   'platform. This is not supported on win32.')

def configure(cnf):  # pylint: disable=R0912
    """Basic configuration of the project based on the operating system and
the available compilers.
    """

    def get_c_standard(env_name, c_std):
        """Define C standard for each compiler"""
        c_std_string = None
        if env_name in ('gcc', 'xlc', 'icc'):
            pref = '-std='
            if c_std == 'c89':
                c_std_string = '{}c89'.format(pref)
            if c_std == 'c99':
                c_std_string = '{}gnu99'.format(pref)
        elif env_name == 'clang':
            c_std_string = '-std={}'.format(c_std)
        elif env_name == 'msvc':
            c_std_string = '/std:c++14'
        return c_std_string or (cnf.fatal('Could not set C-standard'))

    def set_new_basic_env(env_name):
        """Create a new environment based on the base environment"""
        cnf.setenv('')
        tmp_env = cnf.env.derive()
        tmp_env.detach()
        cnf.setenv(env_name, tmp_env)
        cnf.env.env_name = env_name
        c_compiler[host_os] = [cnf.env.env_name]
        cnf.env.c_standard = get_c_standard(cnf.env.env_name,
                                            cnf.env.c_standard)
        cnf.path.get_bld().make_node(env_name).mkdir()

    def check_libs(*libs):
        for lib in libs:
            cnf.check(lib=lib, uselib_store=lib.upper())

    cnf.setenv('')
    cnf.env.host_os = host_os
    cnf.env.c_standard = cnf.options.c_standard
    cnf.env.include_tests = cnf.options.include_tests
    cnf.env.ltests = cnf.options.ltests
    cnf.load('gnu_dirs')
    cnf.env.MAN1DIR = Utils.subst_vars(cnf.options.MAN1DIR, cnf.env)

    min_c = '''\
#include<stdio.h>
int main() {
return 0;
}
'''
    if cnf.options.c_standard == 'c89':
        Logs.warn('C89 does not guarantee 64-bit integers for Lua.')
        Logs.warn('Adding define: LUA_USE_C89')  # TODO
        if host_os == 'win32':
            Logs.warn('This will NOT effect msvc-builds on win32.')
    Logs.info('C standard: {}'.format(cnf.options.c_standard))

    platform_compilers = []
    failed_platform_compilers = []
    if cnf.options.generic:
        if host_os == 'win32':
            cnf.fatal('Generic build not available on win32')
        # TODO generic configuration (gcc, clang)
    elif host_os == 'aix':
        try:  # xlc
            set_new_basic_env('xlc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-brtl,-bexpall']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'dl')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # gcc
            # TODO linker options: -Wl,-brtl,-bexpall
            # TODO when compling with gcc, it must still be used xlc linker
            set_new_basic_env('gcc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'dl')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env('gcc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-brtl,-bexpall']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'dl')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os in ('netbsd', 'openbsd'):
        try:  # gcc
            set_new_basic_env('gcc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env('clang')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == 'freebsd':
        try:  # gcc
            set_new_basic_env('gcc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'readline')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env('clang')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'readline')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == 'linux':
        try:  # gcc
            set_new_basic_env('gcc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'dl', 'readline')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env('clang')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'dl', 'readline')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # icc
            set_new_basic_env('icc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'dl', 'readline')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == 'darwin':
        try:  # gcc
            set_new_basic_env('gcc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'readline')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env('clang')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'readline')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == 'win32':
        cnf.env.WAF_CONFIG_H_PRELUDE = \
            '#if defined(_MSC_VER) && defined(_MSC_FULL_VER)\n' \
            '#pragma warning(disable: 4242 4820 4668 4710 4711)\n' \
            '#endif'
        cnf.write_config_header('config.h')
        try:  # msvc
            set_new_basic_env('msvc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = ['/nologo', cnf.env.c_standard, '/O2', '/Wall']
            cnf.env.CFLAGS += ['/FI'+cnf.env.cfg_files[0]]
            cnf.check_cc(fragment=min_c, execute=True)
            platform_compilers.append(cnf.env.env_name)
            print("Have MANIFEST:", cnf.env.MSVC_MANIFEST)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # gcc
            set_new_basic_env('gcc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # clang
            set_new_basic_env('clang')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.check_cc(fragment=min_c, execute=True)
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == 'cygwin':
        try:  # gcc
            set_new_basic_env('gcc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,--export-all-symbols']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    elif host_os == 'solaris':
        try:  # gcc
            set_new_basic_env('gcc')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'dl')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
        try:  # gcc
            set_new_basic_env('clang')
            cnf.load('compiler_c')
            cnf.env.CFLAGS = [cnf.env.c_standard, '-O2', '-Wall', '-Wextra']
            cnf.env.LINKFLAGS = ['-Wl,-export-dynamic']
            cnf.check_cc(fragment=min_c, execute=True)
            check_libs('m', 'dl')
            platform_compilers.append(cnf.env.env_name)
        except BaseException:
            failed_platform_compilers.append(cnf.env.env_name)
    else:
        Logs.warn('Building generic for platform: {}'.format(host_os))
        cnf.fatal('TODO')

    if not platform_compilers:
        cnf.fatal('Could not configure a single C compiler (tried: {}).\
            '.format(failed_platform_compilers))
    if failed_platform_compilers:
        Logs.warn('Could not configure compilers: {}'.format(
            failed_platform_compilers))

    c_compiler[host_os] = platform_compilers
    Logs.info('Configured compilers: {} on [{}].'.format(c_compiler[host_os],
                                                         host_os))


def build(bld):
    '''Wrapper for the compiler specific build'''
    if not bld.variant:
        if bld.cmd == 'clean':
            Logs.warn('Cleaning for all platforms')
            Options.commands = ['clean_{}'.format(t_cc) for t_cc in \
                c_compiler[host_os]]
            return
    if bld.cmd == 'build':
        bld.fatal('Use a build variant: {}'.format(
            " ".join("build_"+t_cc for t_cc in c_compiler[host_os])))

    bld.clean_files = bld.bldnode.ant_glob(
        '**', excl='.lock* config.log c4che/* build.log', quiet=True,
        generator=True)

    if Utils.is_win32:
        if bld.variant == 'gcc':
            # the DLL produced by gcc is already installed to ${BINDIR}
            pass
        if bld.variant == 'msvc' and bld.env.MSVC_MANIFEST:
            bld.install_files('${BINDIR}', os.path.join('lua', 'luadll.dll'))
            bld.install_files('${BINDIR}',
                              os.path.join('lua', 'luadll.dll.manifest'))
            bld.install_files('${BINDIR}',
                              os.path.join('lua', 'lua.exe.manifest'))
            bld.install_files('${BINDIR}',
                              os.path.join('lua', 'luac.exe.manifest'))

    bld.logger = Logs.make_logger(os.path.join(out, 'build.log'), 'build')
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)
    bld.logger.addHandler(hdlr)
    bld.recurse('lua')
