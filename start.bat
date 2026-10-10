@echo off
REM Get the directory of this script and change to it
cd /d "%~dp0"

REM Set environment variables
set SECRET_KEY=dev
set DEBUG=True
set ALLOWED_HOSTS=localhost,127.0.0.1,testserver

REM Apply migrations and seed the database (only loads if empty)
echo Applying migrations...
.venv\Scripts\python.exe manage.py migrate --noinput

echo Seeding product data (skipped if already present)...
.venv\Scripts\python.exe manage.py loaddata_products

REM Start the server as a detached background process
start "Gundam Store Server" /B .venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload