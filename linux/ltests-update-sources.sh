CS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LUA_VER="5.3.4"
TOP_DIR="$CS\..\.."
TOP_DIR=$(readlink -f $TOP_DIR)
cp $TOP_DIR/lua/lua-$LUA_VER-tests/ltest/*.* $TOP_DIR/lua/lua-$LUA_VER/src\
