@FOR /F "tokens=* USEBACKQ" %%F IN (`where python`) DO @(
    @SET PYTHON=%%F
)
@"%PYTHON%" -x "%~dp0waf" %*
