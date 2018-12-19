#!/usr/bin/env python3
# encoding: utf-8

import sys
import os
import logging

from waflib import Logs, Utils, Options
from waflib.Logs import colors_lst
from waflib.Tools.compiler_c import c_compiler
from waflib.Build import BuildContext, CleanContext, ListContext, StepContext
from waflib.Build import InstallContext, UninstallContext

VERSION = '0.0.1'
APPNAME = 'lua'
top = '.'  # pylint: disable=C0103
out = 'build'  # pylint: disable=C0103

for x in c_compiler[Utils.unversioned_sys_platform()]:
    for y in (BuildContext, CleanContext, ListContext, StepContext,
              InstallContext, UninstallContext):
        name = y.__name__.replace('Context', '').lower()
        class Tmp(y):
            cmd = name + '_' + x
            variant = x

# fix prefix on Windows
if Utils.unversioned_sys_platform() == 'win32':
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


def configure(conf):
    # configure gnudirs the same on all platforms (Unix-like or not)
    conf.load('gnu_dirs')
    conf.env.MAN1DIR = Utils.subst_vars(conf.options.MAN1DIR, conf.env)
    min_c = '''\
#include<stdio.h>
int main() {
return 0;
}
'''
    check_os = Utils.unversioned_sys_platform()
    print(check_os)
    dummy = c_compiler[check_os]
    if check_os == 'win32':
        # msvc
        conf.setenv('msvc')
        c_compiler[check_os] = ['msvc']
        conf.load('compiler_c')
        conf.env.CFLAGS = ['/nologo', '/std:c++14', '/O2', '/Wall']
        conf.env.DEFINES = ['LUA_COMPAT_5_2', '_WIN32']
        conf.check_cc(fragment=min_c, execute=True)
        # gcc
        conf.setenv('gcc')
        c_compiler[check_os] = ['gcc']
        conf.load('compiler_c')
        conf.env.CFLAGS = ['-std=gnu99', '-O2', '-Wall', '-Wextra']
        conf.env.DEFINES = ['LUA_COMPAT_5_2']
        conf.check_cc(fragment=min_c, execute=True)
        conf.check(lib='m', cflags='-Wall', uselib_store='M')
        # clang
        conf.setenv('clang')
        c_compiler[check_os] = ['clang']
        conf.load('compiler_c')
        conf.env.CFLAGS = ['-std=c99', '-O2', '-Wall', '-Wextra']
        conf.env.DEFINES = ['LUA_COMPAT_5_2']
        conf.check_cc(fragment=min_c, execute=True)
    elif check_os == 'cygwin':
        conf.fatal('TODO')
    elif check_os == 'linux':
        print(1)
        # gcc
        conf.setenv('gcc')
        c_compiler[check_os] = ['gcc']
        conf.load('compiler_c')
        conf.env.CFLAGS = ['-std=gnu99', '-O2', '-Wall', '-Wextra']
        conf.env.DEFINES = ['LUA_COMPAT_5_2']
        conf.check_cc(fragment=min_c, execute=True)
        conf.check(lib='m', cflags='-Wall', uselib_store='M')
        # clang
        conf.setenv('clang')
        c_compiler[check_os] = ['clang']
        conf.load('compiler_c')
        conf.env.CFLAGS = ['-std=c99', '-O2', '-Wall', '-Wextra']
        conf.env.DEFINES = ['LUA_COMPAT_5_2']
        conf.check_cc(fragment=min_c, execute=True)
        conf.check(lib='m', cflags='-Wall', uselib_store='M')
    # reset to all supported compilers
    c_compiler[check_os] = dummy
    Logs.pprint(
        'NORMAL',
        f'\nThe following compilers are configured: {c_compiler[check_os]}')
    for tmp_cc in c_compiler[check_os]:
        conf.setenv(tmp_cc)
        Logs.pprint('NORMAL', f'--> Using {colors_lst["GREEN"]}{conf.env.CC_NAME}{colors_lst["NORMAL"]} on {colors_lst["GREEN"]}{conf.env.DEST_OS}{colors_lst["NORMAL"]}')  # pylint: disable=C0301
        Logs.pprint('NORMAL', f'    --> CFLAGS:     {colors_lst["GREEN"]}{" ".join(conf.env.CFLAGS) or colors_lst["NORMAL"]+"(None)"}{colors_lst["NORMAL"]}')  # pylint: disable=C0301
        Logs.pprint('NORMAL', f'    --> DEFINES:    {colors_lst["GREEN"]}{" ".join(conf.env.DEFINES) or colors_lst["NORMAL"]+"(None)"}{colors_lst["NORMAL"]}')  # pylint: disable=C0301
        Logs.pprint('NORMAL', f'    --> LDFLAGS:    {colors_lst["GREEN"]}{" ".join(conf.env.LDFLAGS) or colors_lst["NORMAL"]+"(None)"}{colors_lst["NORMAL"]}')  # pylint: disable=C0301
        Logs.pprint('NORMAL', f'    --> LINKFLAGS:  {colors_lst["GREEN"]}{" ".join(conf.env.LINKFLAGS) or colors_lst["NORMAL"]+"(None)"}{colors_lst["NORMAL"]}')  # pylint: disable=C0301
    print()

def build(bld):
    '''Wrapper for the compiler specific build'''
    if not bld.variant:
        if bld.cmd == 'clean':
            Logs.warn('Cleaning for all platforms')
            Options.commands = [f'clean_{tmp_cc}' for tmp_cc in c_compiler[Utils.unversioned_sys_platform()]]  # pylint: disable=C0301
            return
    if bld.cmd == 'build':
        bld.fatal('Use a build variant: ' + f'{" ".join("build_"+tmp_cc for tmp_cc in c_compiler[Utils.unversioned_sys_platform()])}')  # pylint: disable=C0301

    bld.clean_files = bld.bldnode.ant_glob(
        '**', excl='.lock* config.log c4che/* build.log', quiet=True,
        generator=True)

    bld.logger = Logs.make_logger(os.path.join(out, 'build.log'), 'build')
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)
    bld.logger.addHandler(hdlr)
    bld.recurse('lua')

def test(bld):
    bld.recurse('lua')
