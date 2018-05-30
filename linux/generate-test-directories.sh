CS="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LUA_VER="5.3.4"
TOP_DIR="$CS/.."
cd $TOP_DIR
pwd
TESTS=lua-$LUA_VER-tests
cd lua/$TESTS
cd libs
mkdir P1
