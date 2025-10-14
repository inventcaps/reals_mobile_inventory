@echo off
echo ========================================
echo   Real's Inventory - Phone Testing
echo ========================================
echo.
echo Your WiFi IP: 192.168.1.197
echo Server Port: 8001
echo.
echo Access from phone:
echo http://192.168.1.197:8001
echo.
echo ========================================
echo Starting server...
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8001
