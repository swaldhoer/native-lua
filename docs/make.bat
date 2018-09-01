@REM Make sure to run in correct directory
@CALL :NORMALIZEPATH "%~dp0..\"
@SET normpath_ret=%normpath%
@if not %normpath_ret%==%__CD__% (
    @echo Script must be run in root directory:
    @echo "%normpath_ret%"
    @exit /b 1
)

@set SRC_DIR=docs
@set BLD_DIR=build\docs

@REM Remove rendered documentation
@if "%1"=="clean" (
    @echo Cleaning...
    @rmdir /s /q %BLD_DIR% > nul 2>&1
    @echo [32mclean succeeded.[0m
    @exit /b %errorlevel%
)

@REM Make sure sphinx exists
@set SPHINX_BUILD=sphinx-build
@where /q %SPHINX_BUILD%
@if errorlevel 1 (
    @echo %SPHINX_BUILD% is missing in PATH.
    @exit /b 1
)

@REM Render the documentation
@%SPHINX_BUILD% -b html %SRC_DIR% %BLD_DIR%
@if %errorlevel% equ 0 (
    @echo [32mbuild succeeded.[0m
)
@exit /b %errorlevel%

@REM see https://stackoverflow.com/a/33404867/4408275
:NORMALIZEPATH
  @set normpath=%~dpfn1
  @exit /B
