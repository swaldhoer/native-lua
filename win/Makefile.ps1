<#
.SYNOPSIS
Provides most of the commands supported by the Makefile (e.g., building,
installing), but with some Windows specific adaptions.

.DESCRIPTION
Parameters are:
    - build:        Build the lua interpreter and compiler
    - clean:        Clean the build directory
    - install:      Install the interpreter, compiler etc.; assumes a
                    successfull build
    - uninstall:    Removes the interpreter, compiler etc.;
    - echo:         echos the configuration
    - pc:           echos the version

License:
    - MIT License
    - for details see .\native-lua\LICENSE

.EXAMPLE
.\Makefile.ps1 build
builds the blabkla

.EXAMPLE
.\Makefile.ps1 clean
cleans the blabkla

.NOTES
MIT License
Copyright (c) 2018 swaldhoer
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

.LINK
https://github.com/swaldhoer/native-lua

#>

function validate_arguments_and_options ($c) {
    $valid_all = $valid_cmds + $valid_opts
    $err_bit = 0
    foreach ($a in $c) {
        if ($valid_all -notcontains $a) {
            Write-Host "'$a' is not a valid command"
            $err_bit++
        } else {
            if ($a -clike "x86" -or $a -clike "x64" ) {
                $Platform = $a
            }
            if ($a -clike "Debug" -or $a -clike "Release" ) {
                $Configuration = $a
            } elseif ($a -clike "debug" -or $a -clike "release" ) {
                $err_bit++
                $first_upper = $a[0].ToString().ToUpper()
                $x = $first_upper + $a.substring(1)
                Write-Host "Your wrote ""$a"", did you mean ""$x""?" `
                    -ForegroundColor Yellow
            }
        }
    }

    if ($err_bit -gt 0) {
        Write-Host "Exiting script since argument errors..." `
            -ForegroundColor Red
        exit
    }

    return $Platform, $Configuration
}

function _test {
    Write-Host "$BUILD_DIR\lua\$PLAT_CONF\lua.exe -v" -ForegroundColor Green
    & $BUILD_DIR\lua\$PLAT_CONF\lua.exe -v
}

function _clean {
    $clean_cmd = "$BUILD_CMD_s && " `
        + "msbuild .\..\msbuild\lua.sln " `
        + "/property:Platform=$Platform " `
        + "/property:Configuration=$Configuration " `
        + "/t:clean " `
        + "& exit"
    cmd /k "$clean_cmd"
}

function _build {
    $build_cmd = "$BUILD_CMD_s && " `
        + "msbuild .\..\msbuild\lua.sln " `
        + "/property:Platform=$Platform " `
        + "/property:Configuration=$Configuration " `
        + "/verbosity:normal " `
        + "& exit"
    cmd /k "$build_cmd"
}

function _install {
    Write-Host "Installing Lua $R ($Platform-$Configuration)`n"
    Write-Host "Installing files..."
    foreach ($sdir in $dirs) {
        New-Item -Force -ItemType Directory -Path $sdir | Out-Null
    }
    # Install bin
    Copy-Item -Path "$BUILD_DIR\lua\$PLAT_CONF\lua.exe" `
        -Destination $INSTALL_BIN -force
    Copy-Item -Path "$BUILD_DIR\lua\$PLAT_CONF\dliblua.dll" `
        -Destination $INSTALL_BIN -force
    Copy-Item -Path "$BUILD_DIR\luac\$PLAT_CONF\luac.exe" `
        -Destination $INSTALL_BIN -force
    # Install includes
    foreach ($sfile in $TO_INC) {
        Copy-Item -Path "$TOP_DIR\lua\lua-$R\src\$sfile" `
            -Destination $INSTALL_INC -force
    }
    # Install lib
    Copy-Item -Path "$BUILD_DIR\sliblua\$PLAT_CONF\sliblua.lib" `
        -Destination $INSTALL_LIB -force
    # Install man
    foreach ($sfile in $TO_MAN) {
        Copy-Item -Path "$TOP_DIR\lua\lua-$R\doc\$sfile" `
            -Destination $INSTALL_MAN -force
    }
    Write-Host "Done installing files...`n" -ForegroundColor Green

    Write-Host "Setting environment variables..."
    $LUA_DIR = "LUA_DIR"
    if (-not (Test-Path env:$LUA_DIR)) {
        Write-Host "Add `$LUA_DIR to `$env"
        [System.Environment]::SetEnvironmentVariable($LUA_DIR, $INSTALL_BIN, `
               [System.EnvironmentVariableTarget]::User)
        [System.Environment]::SetEnvironmentVariable($LUA_DIR, $INSTALL_BIN, `
               [System.EnvironmentVariableTarget]::Process)
    } else {
        Write-Host "'$LUA_DIR' already in `$env" -ForegroundColor Yellow
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
        Write-Host "'$LUA_CPATH' already in `$env"  -ForegroundColor Yellow
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
        Write-Host "'$LUA_PATH' already in `$env"  -ForegroundColor Yellow
    }

    if ($env:Path -like "*$INSTALL_BIN*") {
        Write-Host "'$INSTALL_BIN' already in `$env:Path" `
            -ForegroundColor Yellow
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
    Write-Host "Done setting environment variables...`n" -ForegroundColor Green

    Write-Host "LUA_DIR:    $env:LUA_DIR"
    Write-Host "LUA_CPATH:  $env:LUA_CPATH"
    Write-Host "LUA_PATH:   $env:LUA_PATH"
    if ($env:Path -like "*$INSTALL_BIN*") {
        Write-Host "PATH:       OK"
    }

    Write-Host "Successfully installed Lua $R`n" -ForegroundColor Green
    $LUA_VARS = "# helper script for dot-sourcing
    `$env:LUA_DIR = ""$INSTALL_BIN""
    `$env:LUA_CPATH = ""$LUA_CPATH_CONTENT""
    `$env:LUA_PATH = ""$LUA_PATH_CONTENT""
    `$env:Path += "";$INSTALL_BIN"""
    Out-File -FilePath $INSTALL_TOP\luaprofile.ps1 -InputObject $LUA_VARS `
        -Encoding ASCII -Width 79

    Write-Host "Run `n    . $INSTALL_TOP\luaprofile.ps1`nto use Lua in this" `
        "session.`n"
}

function _uninstall {
    Write-Host "Uninstalling Lua $R ($Platform-$Configuration)`n"

    Write-Host "Removing files..."
    if (Test-Path -PathType Any $INSTALL_TOP) {
        Remove-Item -Recurse -Force $INSTALL_TOP
    } else {
        Write-Host "Nothing to remove for $INSTALL_TOP" -ForegroundColor Yellow
    }
    Write-Host "Done removing files...`n" -ForegroundColor Green

    Write-Host "Removing environment variables..."
    $lua_env_vars = 'LUA_DIR', 'LUA_CPATH', 'LUA_PATH'
    foreach ($lua_var in $lua_env_vars) {
        if (Test-Path env:$lua_var) {
            Write-Host "Remove $lua_var from `$env"
            [System.Environment]::SetEnvironmentVariable($lua_var, $null,
                [System.EnvironmentVariableTarget]::User)
            [System.Environment]::SetEnvironmentVariable($lua_var, $null, `
                [System.EnvironmentVariableTarget]::Process)
        } else {
            Write-Host "Nothing to remove for '$lua_var' from `$env" `
                -ForegroundColor Yellow
        }
    }

    if ($env:Path -like "*$INSTALL_BIN*") {
        Write-Host "Remove `$INSTALL_BIN from `$env:Path"
        $Old_Path = (Get-ItemProperty -Path 'Registry::HKEY_CURRENT_USER\Environment' -Name Path).Path
        $rep_path = $Old_Path.Replace("$INSTALL_BIN;", "")
        $rep_path = $rep_path.Replace("$INSTALL_BIN", "")
        Set-ItemProperty -Path 'Registry::HKEY_CURRENT_USER\Environment' -Name PATH -Value ($rep_path) -Verbose -PassThru|fl | Out-Null
    } else {
        Write-Host "Nothing to remove for `$INSTALL_BIN in `$env:Path" `
            -ForegroundColor Yellow
    }
    Write-Host "Done removing environment variables...`n" -ForegroundColor Green

    Write-Host "Successfully removed Lua $R`n" -ForegroundColor Green
}

function _pc {
    Write-Host "version=$R"
    Write-Host "prefix=$INSTALL_TOP"
    Write-Host "libdir=$INSTALL_LIB"
    Write-Host "includedir=$INSTALL_INC"
}

function _echo {
    Write-Host "PLAT= $PLAT"
    Write-Host "V= $V"
    Write-Host "R= $R"
    Write-Host "TO_BIN= $TO_BIN"
    Write-Host "TO_INC= $TO_INC"
    Write-Host "TO_LIB= $TO_LIB"
    Write-Host "TO_MAN= $TO_MAN"
    Write-Host "INSTALL_TOP= $INSTALL_TOP"
    Write-Host "INSTALL_BIN= $INSTALL_BIN"
    Write-Host "INSTALL_INC= $INSTALL_INC"
    Write-Host "INSTALL_LIB= $INSTALL_LIB"
    Write-Host "INSTALL_MAN= $INSTALL_MAN"
    Write-Host "INSTALL_LMOD= $INSTALL_LMOD"
    Write-Host "INSTALL_CMOD= $INSTALL_CMOD"
    Write-Host "INSTALL_EXEC= $INSTALL_EXEC"
    Write-Host "INSTALL_DATA= $INSTALL_DATA"
}

################################# Script entry #################################
$cs = split-path $PSCommandPath -Leaf
if ($args.Count -eq 0) {
    Write-Host "Run '.\$cs -h' for instructions."
    exit
}

if ($args -contains "-h" -or
    $args -contains "--help" -or
    $args -contains "/h" -or
    $args -contains "/help") {
    help $PSCommandPath -full
    exit
}


$ErrorActionPreference = "Stop"

$PLAT = $Env:OS

$INSTALL_TOP = "C:\Lua"
$INSTALL_BIN = Join-Path "$INSTALL_TOP" "\bin"
$INSTALL_INC = Join-Path "$INSTALL_TOP" "include"
$INSTALL_LIB = Join-Path "$INSTALL_TOP" "lib"
$INSTALL_MAN = Join-Path "$INSTALL_TOP" "man\man1"
$INSTALL_LMOD = Join-Path "$INSTALL_TOP" "share\lua\$V"
$INSTALL_CMOD = Join-Path "$INSTALL_TOP" "lib\lua\$V"
$dirs = ($INSTALL_TOP, $INSTALL_BIN, $INSTALL_INC, $INSTALL_LIB, `
    $INSTALL_MAN, $INSTALL_LMOD, $INSTALL_CMOD)

$TO_BIN = "lua.exe", "dliblua.dll", "luac.exe"
$TO_INC = "lua.h", "luaconf.h", "lualib.h", "lauxlib.h", "lua.hpp"
$TO_LIB = "liblua.lib"
$TO_MAN = "lua.1", "luac.1"

$V = "5.3"
$R = "$V.4"

$BUILD_CMD = """C:\Program Files (x86)\Microsoft Visual Studio\2017\" `
    + "Community\Common7\Tools\VsDevCmd.bat"""
$BUILD_CMD_s = $BUILD_CMD + " > nul 2>&1"

$valid_cmds = "clean", "test", "build", "install", "uninstall", "echo", "pc"
$valid_opts = "x64", "x86", "Debug", "Release"
$args_ws = $args

if ($ENV:PROCESSOR_ARCHITECTURE -eq "AMD64") {
    $Platform = "x64"
} else {
    $Platform = "x86"
}
$Configuration="Release"
$conf_vars = validate_arguments_and_options $args
$Platform = $conf_vars[0]
$Configuration = $conf_vars[1]

$TOP_DIR = Resolve-Path $PSScriptRoot\..
$BUILD_DIR = "$TOP_DIR\build"
$PLAT_CONF = "$Platform\$Configuration"

# Now we only have valid arguments
if ($args -contains "clean") { _clean }

if ($args -contains "build") { _build }

if ($args -contains "install") { _install }

if ($args -contains "uninstall") { _uninstall }

if ($args -contains "test") { _test }

if ($args -contains "dummy") { }

if ($args -contains "echo") { _echo }

if ($args -contains "pc") { _pc }
