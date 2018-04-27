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

Write-Host "Installing Lua $R ($Platform-$Configuration)`n"

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

Write-Host "Installing files..."

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
Write-Host "Done installing files...`n"




Write-Host "Setting environment variables..."
$LUA_DIR = "LUA_DIR"
if (-not (Test-Path env:$LUA_DIR)) {
    Write-Host "Add `$LUA_DIR to `$env"
    [System.Environment]::SetEnvironmentVariable($LUA_DIR, $INSTALL_BIN, `
           [System.EnvironmentVariableTarget]::User)
    [System.Environment]::SetEnvironmentVariable($LUA_DIR, $INSTALL_BIN, `
           [System.EnvironmentVariableTarget]::Process)
} else {
    Write-Host "'$LUA_DIR' already in `$env"
}

$LUA_CPATH = "LUA_CPATH"
$LUA_CPATH_CONTENT = "?.dll;%LUA_DIR%\?.dll"
if (-not (Test-Path env:$LUA_CPATH)) {
    Write-Host "Add `$LUA_CPATH to `$env"
    [System.Environment]::SetEnvironmentVariable($LUA_CPATH, `
        $LUA_CPATH_CONTENT, [System.EnvironmentVariableTarget]::User)
    [System.Environment]::SetEnvironmentVariable($LUA_CPATH, `
        $LUA_CPATH_CONTENT, [System.EnvironmentVariableTarget]::Process)
} else {
    Write-Host "'$LUA_CPATH' already in `$env"
}

$LUA_PATH = "LUA_PATH"
$LUA_PATH_CONTENT = "?.lua;%LUA_DIR%\lua\?.lua"
if (-not (Test-Path env:$LUA_PATH)) {
    Write-Host "Add `$LUA_PATH to `$env"
    [System.Environment]::SetEnvironmentVariable("LUA_PATH", `
        $LUA_PATH_CONTENT, [System.EnvironmentVariableTarget]::User)
    [System.Environment]::SetEnvironmentVariable("LUA_PATH", `
        $LUA_PATH_CONTENT, [System.EnvironmentVariableTarget]::Process)
} else {
    Write-Host "'$LUA_PATH' already in `$env"
}

if ($env:Path -like "*$INSTALL_BIN*") {
    Write-Host "'$INSTALL_BIN' already in `$env:Path"
} else {
    Write-Host "Add `$INSTALL_BIN to `$env:Path"
    if ($env:Path.Substring($env:Path.Length-1) -eq ";") {
        $sep = ""
    } else {
        $sep = ";"
    }
    $Old_Path=(Get-ItemProperty -Path 'Registry::HKEY_CURRENT_USER\Environment' -Name Path).Path
    Set-ItemProperty -Path 'Registry::HKEY_CURRENT_USER\Environment' -Name PATH -Value ($Old_Path += ';C:\Lua\bin') -Verbose -PassThru|fl | Out-Null
}
Write-Host "Done setting environment variables...`n"

Write-Host "LUA_DIR:    $env:LUA_DIR"
Write-Host "LUA_CPATH:  $env:LUA_CPATH"
Write-Host "LUA_PATH:   $env:LUA_PATH"
if ($env:Path -like "*$INSTALL_BIN*") {
    Write-Host "PATH:       OK"
}

Write-Host "Successfully installed Lua $R`n"
$LUA_VARS = "# helper script for dot-sourcing
`$env:LUA_DIR = ""$INSTALL_BIN""
`$env:LUA_CPATH = ""$LUA_CPATH_CONTENT""
`$env:LUA_PATH = ""$LUA_PATH_CONTENT""
`$env:Path += "";$INSTALL_BIN"""
Out-File -FilePath $INSTALL_TOP\luaprofile.ps1 -InputObject $LUA_VARS -Encoding ASCII -Width 79

Write-Host "Run `n    . $INSTALL_TOP\luaprofile.ps1`n to use Lua in this session."
