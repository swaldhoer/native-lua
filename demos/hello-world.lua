#!/usr/bin/env lua

-- SPDX-License-Identifier: MIT

print("Hello world!")

io.write("Hello ")
io.write("world ")
io.write("again!\n")

hello = "Hello"
world = "world"
times_three = "a third time!"

print(hello .. " " .. world .. " " .. times_three)

print(table.concat({hello, world, times_fourth}, " "))
