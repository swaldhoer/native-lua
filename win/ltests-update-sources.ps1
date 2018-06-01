$CS=Split-Path $PSCommandPath
$LUA_VER="5.3.4"
$TOP_DIR=Join-Path $CS ".."
$TOP_DIR=Resolve-Path $TOP_DIR
Copy-Item $TOP_DIR\lua\lua-$LUA_VER-tests\ltests\* $TOP_DIR\lua\lua-$LUA_VER\src\
