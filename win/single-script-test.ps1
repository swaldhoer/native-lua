$ErrorActionPreference = "Stop"
lua -v
$TOP_DIR = Resolve-Path $PSScriptRoot\..
$test_dir = "$TOP_DIR\lua\lua-5.3.4-tests\"

$test_files = `
    "api.lua", `
    "attrib.lua", `
    "big.lua", `
    "bitwise.lua", `
    "calls.lua", `
    "closure.lua", `
    "code.lua", `
    "constructs.lua", `
    "coroutine.lua", `
    "db.lua", `
    "errors.lua", `
    "events.lua", `
    "files.lua", `
    "gc.lua", `
    "goto.lua", `
    "literals.lua", `
    "locals.lua", `
    "main_win.lua", `
    "math.lua", `
    "nextvar.lua", `
    "pm.lua", `
    "sort.lua", `
    "strings.lua", `
    "tpack.lua", `
    "utf8.lua", `
    "vararg.lua", `
    "verybig.lua"
    
Foreach ($i in $test_files) {
    $cur_test_file = $test_dir + $i
    Write-Host "Testing: $cur_test_file"
    PowerShell.exe 'cmd.exe /c "lua $cur_test_file"'
    if ($? -ne "True") {
        exit
    }
}
