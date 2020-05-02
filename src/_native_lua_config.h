/* SPDX-License-Identifier: MIT */

/**
 * @file    _native_lua_config.h
 * @author  the native Lua Authors
 * @date    2020-05-02
 * @brief   native Lua configuration file
 * @details This file is either included in a header file or the source file if
 *          no header file exists. This file is for native Lua specific
 *          configurations.
 */

#ifndef NATIVE_LUA_CONFIG_H_
#define NATIVE_LUA_CONFIG_H_

#define NATIVE_LUA_MSG " [" NATIVE_LUA_PRE_MSG " (" NATIVE_LUA_VERSION"), " NATIVE_LUA_REPO"]"

#if defined(_MSC_VER) && defined(_MSC_FULL_VER)
#pragma warning(disable: 4242 4820 4668 4710 4711 5045)
/* Disable C5045 (see https://docs.microsoft.com/de-de/cpp/error-messages/compiler-warnings/c5045) */
/* we are compiling with /Qspectre */
#endif

#endif /* NATIVE_LUA_CONFIG_H_ */
