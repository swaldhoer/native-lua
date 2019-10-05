#!/usr/bin/env lua

-- SPDX-License-Identifier: MIT

array = {}
printable = ""

size = 10

math.randomseed(os.time())
for i=1, size do
  val = math.random(0, 9)
  array[i] = val
  printable = printable .. val .. " "
end

print("Unsorted array:      " .. printable)

for i=1, size do
  for k=1, i-1 do
    if array[i] > array[k] then
      array[i], array[k] = array[k], array[i]
    end
  end
end

printable = ""
for i=1, size do
  printable = printable .. array[i] .. " "
end
print("Top sorted array:    " .. printable)

printable = ""
for i=size, 1, -1 do
  for k=1, i-1, 1 do
    if array[k] > array[i] then
      array[i], array[k] = array[k], array[i]
    end
  end
end

for i=1, size do
  printable = printable .. array[i] .. " "
end

print("Bottom sorted array: " .. printable)
