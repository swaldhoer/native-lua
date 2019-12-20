@FOR /F "tokens=* USEBACKQ" %%F IN (`where python`) DO @(
    @IF "%%F" neq "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" @(
        @SET PYTHON=%%F
    )
)
@"%PYTHON%" -x "%~dp0waf" %*
