#!/usr/bin/env python3
# encoding: utf-8

import sys
import os
import logging

from waflib import Logs, Utils
from waflib.Tools.compiler_c import c_compiler

VERSION = '0.0.1'
APPNAME = 'lua'
top = '.'  # pylint: disable=C0103
out = 'build'  # pylint: disable=C0103

# use gcc on all platforms, except for windows, there use msvc primarily and
# then gcc
for x in c_compiler:
    if x == 'win32':
        c_compiler['win32'] = ['msvc', 'gcc']
    else:
        c_compiler[x] = ['gcc']

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
    conf.load('gnu_dirs')
    conf.env.MAN1DIR = Utils.subst_vars(conf.options.MAN1DIR, conf.env)
    conf.load('compiler_c')

    # set compiler specific, os independent CFLAGS
    # All CFLAGS specified are overwritten, as we decide how to compile
    if conf.env.CC_NAME == 'gcc':
        conf.env.CFLAGS = ['-std=gnu99', '-O2', '-Wall', '-Wextra']
        conf.check(lib='m', cflags='-Wall', uselib_store='M')
    if conf.env.CC_NAME == 'msvc':
        conf.env.CFLAGS = ['/nologo', '/std:c++14', '/O2', '/Wall']

    if conf.env.DEST_OS == 'win32':
        conf.env.DEFINES += ['_WIN32']
        if conf.env.CC_NAME == 'msvc':
            pass
        if conf.env.CC_NAME == 'gcc':
            pass
    else:
        pass

    Logs.info(f'--> Using {conf.env.CC_NAME} on {conf.env.DEST_OS}')
    Logs.info(f'--> CFLAGS: {" ".join(conf.env.CFLAGS)}')
    Logs.info(f'--> LDFLAGS: {" ".join(conf.env.LDFLAGS)}')
    Logs.info(f'--> LINKFLAGS: {" ".join(conf.env.LINKFLAGS)}')


def build(bld):
    bld.clean_files = bld.bldnode.ant_glob(
        '**', excl='.lock* config.log c4che/* build.log', quiet=True,
        generator=True)

    bld.logger = Logs.make_logger(os.path.join(out, 'build.log'), 'build')
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(message)s')
    hdlr.setFormatter(formatter)
    bld.logger.addHandler(hdlr)
    bld.recurse('lua')
