@echo off
REM === SCP Copy Script with Offline Dependencies ===
REM Edit the following variables for your remote server
set REMOTE_USER=admin.local
set REMOTE_HOST=10.10.30.66


echo Copying Presentator to Raspberry Pi...
echo ========================================


scp app.py %REMOTE_USER%@%REMOTE_HOST%:/home/%REMOTE_USER%/http-server-python/Presentator/
scp install.py %REMOTE_USER%@%REMOTE_HOST%:/home/%REMOTE_USER%/http-server-python/Presentator/
scp requirements.txt %REMOTE_USER%@%REMOTE_HOST%:/home/%REMOTE_USER%/http-server-python/Presentator/
scp -r web/* %REMOTE_USER%@%REMOTE_HOST%:/home/%REMOTE_USER%/http-server-python/Presentator/web/
scp -r slideshows/* %REMOTE_USER%@%REMOTE_HOST%:/home/%REMOTE_USER%/http-server-python/Presentator/slideshows/
scp -r src/* %REMOTE_USER%@%REMOTE_HOST%:/home/%REMOTE_USER%/http-server-python/Presentator/src/


REM Copy Linux offline packages and installation scripts
echo Copying Linux offline dependencies...

if exist "offline_packages_linux" (
    scp -r offline_packages_linux/* %REMOTE_USER%@%REMOTE_HOST%:/home/%REMOTE_USER%/http-server-python/Presentator/offline_packages_linux/
    scp install_offline_linux.sh %REMOTE_USER%@%REMOTE_HOST%:/home/%REMOTE_USER%/http-server-python/Presentator/
)