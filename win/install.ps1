Param(
  [string]$Platform,
  [string]$Configuration="Release"
)

$ErrorActionPreference = "Stop"

if ($Platform -eq "") {
    if ($ENV:PROCESSOR_ARCHITECTURE -eq "AMD64") {
        $Platform = "x64"
    } else {
        $Platform = "x86"
    }
}

# Lua version and release
$V = "5.3"
$R = "$V.4"

Write-Host "Installing Lua $R ($Platform-$Configuration)"

$TOP_DIR = Resolve-Path $PSScriptRoot\..

$INSTALL_TOP = "C:\Lua"
$INSTALL_BIN = Join-Path "$INSTALL_TOP" "\bin"
$INSTALL_INC = Join-Path "$INSTALL_TOP" "include"
$INSTALL_LIB = Join-Path "$INSTALL_TOP" "lib"
$INSTALL_MAN = Join-Path "$INSTALL_TOP" "man\man1"
$INSTALL_LMOD = Join-Path "$INSTALL_TOP" "share\lua\$V"
$INSTALL_CMOD = Join-Path "$INSTALL_TOP" "lib\lua\$V"
$dirs = ($INSTALL_TOP, $INSTALL_BIN, $INSTALL_INC, $INSTALL_LIB, `
    $INSTALL_MAN, $INSTALL_LMOD, $INSTALL_CMOD)

foreach ($sdir in $dirs) {
    New-Item -Force -ItemType Directory -Path $sdir | Out-Null
}

# Some simplifications
$BUILD_DIR = "$TOP_DIR\build"
$PLAT_CONF = "$Platform\$Configuration"

Write-Host "Installing Files"

# Install files
$TO_BIN = "lua.exe", "dliblua.dll", "luac.exe"
$TO_INC = "lua.h", "luaconf.h", "lualib.h", "lauxlib.h", "lua.hpp"
$TO_LIB = "liblua.lib"
$TO_MAN = "lua.1", "luac.1"

# Install bin
Copy-Item -Path "$BUILD_DIR\lua\$PLAT_CONF\lua.exe" `
    -Destination $INSTALL_BIN -force
Copy-Item -Path "$BUILD_DIR\lua\$PLAT_CONF\dliblua.dll" `
    -Destination $INSTALL_BIN -force
Copy-Item -Path "$BUILD_DIR\luac\$PLAT_CONF\luac.exe" `
    -Destination $INSTALL_BIN -force

# Install includes
foreach ($sfile in $TO_INC) {
    Copy-Item -Path "$TOP_DIR\lua\lua-$R\src\$sfile" -Destination $INSTALL_INC `
        -force
}

# Install lib
Copy-Item -Path "$BUILD_DIR\sliblua\$PLAT_CONF\sliblua.lib" `
    -Destination $INSTALL_LIB -force

# Install man
foreach ($sfile in $TO_MAN) {
    Copy-Item -Path "$TOP_DIR\lua\lua-$R\doc\$sfile" -Destination $INSTALL_MAN `
        -force
}

Write-Host "Setting environment variables"
[System.Environment]::SetEnvironmentVariable("LUA_DIR", $INSTALL_BIN, `
    [System.EnvironmentVariableTarget]::User)
[System.Environment]::SetEnvironmentVariable("LUA_CPATH", `
    "?.dll;%LUA_DIR%\?.dll", [System.EnvironmentVariableTarget]::User)
[System.Environment]::SetEnvironmentVariable("LUA_PATH", `
    "?.lua;%LUA_DIR%\lua\?.lua", [System.EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Lua\bin", `
    [EnvironmentVariableTarget]::User)

Write-Host "LUA_DIR:    $env:LUA_DIR"
Write-Host "LUA_CPATH:  $env:LUA_CPATH"
Write-Host "LUA_PATH:   $env:LUA_PATH"
Write-Host "PATH:       $env:Path"

Write-Host "Successfully installed Lua $R`n"
