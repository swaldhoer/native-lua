#!/usr/bin/env lua

-- SPDX-License-Identifier: MIT

-- use the debug library to get information on the script location
function get_script_info()
  local info = debug.getinfo(1,'S')
  local script_rel_path = info.short_src

  local current_dir
  if package.config:sub(1,1) == "/" then
    current_dir = io.popen"pwd":read'*l'
  else
    current_dir = io.popen"cd":read'*l'
  end

  local script_abs_path = current_dir .. package.config:sub(1,1) .. script_rel_path

  for i in string.gmatch(info.source, "[^" .. package.config:sub(1,1) .. "]+") do
    local script_name = i
  end

  return script_abs_path, script_rel_path, script_name
end

script_abs_path, script_rel_path, script_name = get_script_info()

-- open the file and check if it really exists
file = io.open(script_abs_path, "r")
io.write("File \"" .. script_abs_path .. "\"")
if not file then
  io.write(" does not exist.\n")
  os.exit(1)
else
  io.write(" exists.\n")
end
io.close(file)

-- or better use assert() on file opening
-- then read the complete file and close the file
f = assert(io.open(script_rel_path, "r"))
content = f:read("*all")
f:close()
