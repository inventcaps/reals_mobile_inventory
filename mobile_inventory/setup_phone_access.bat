@echo off
echo ========================================
echo   Setup Phone Access
echo ========================================
echo.

REM Get WiFi IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address" ^| findstr "192.168"') do (
    set IP=%%a
)

REM Remove leading space
set IP=%IP: =%

echo Your WiFi IP: %IP%
echo.

REM Update .env file
echo Updating .env file...
echo # Django Settings > .env
echo SECRET_KEY=django-insecure-(au!8znc(9t!+up-=!qu$*c8rqsfzk_qdbn^&yek_ao^^_3tfrek >> .env
echo DEBUG=True >> .env
echo. >> .env
echo # Database Configuration >> .env
echo DB_NAME=reals_local >> .env
echo DB_USER=postgres >> .env
echo DB_PASSWORD=admin >> .env
echo DB_HOST=localhost >> .env
echo DB_PORT=5432 >> .env
echo. >> .env
echo # Allowed Hosts (comma-separated) >> .env
echo ALLOWED_HOSTS=localhost,127.0.0.1,%IP% >> .env

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Access from phone:
echo http://%IP%:8001
echo.
echo Next step: Run "run_for_phone.bat"
echo.
pause
