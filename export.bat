@echo off
rem Function to check if Poetry is installed
call :check_poetry_installed
if errorlevel 1 exit /b 1

rem Get the optional parameter if provided
set "environment=%~1"

rem Run the appropriate export command based on the parameter
call :export_dependencies "%environment%"

exit /b 0

:check_poetry_installed
poetry --version >nul 2>&1
if errorlevel 1 (
    echo Poetry is not installed. Please install it and try again.
    exit /b 1
)
exit /b 0

:export_dependencies
setlocal
set "option=%~1"

if not "%option%"=="--prod" if not "%option%"=="--dev-binary" (
    echo Exporting development dependencies using Poetry...
    poetry export --with dev,test,c -f requirements.txt -o requirements\local.txt
)

if "%option%"=="--dev-binary" (
    echo Exporting non-C development dependencies using Poetry...
    poetry export --with dev,test,binary -f requirements.txt -o requirements\local.txt
)

if not "%option%"=="--dev" if not "%option%"=="--dev-binary" (
    echo Exporting production dependencies using Poetry...
    poetry export --with production,c -f requirements.txt -o requirements\production.txt
)

endlocal
exit /b 0
