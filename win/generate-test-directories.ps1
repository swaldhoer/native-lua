$CS=Split-Path $PSCommandPath
$LUA_VER="5.3.4"
$TOP_DIR=Join-Path $CS ".."
$TOP_DIR=Resolve-Path $TOP_DIR

$TESTS= Join-Path "lua" "lua-$LUA_VER-tests"
Set-Location -Path $TESTS
Set-Location -Path libs
New-Item -ItemType directory -Path P1
# TODO run msbuild
