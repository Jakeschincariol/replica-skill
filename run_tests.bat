@echo off
setlocal

set PY_CMD=
where py >nul 2>&1 && set PY_CMD=py -3
if not defined PY_CMD (
    where python >nul 2>&1 && set PY_CMD=python
)
if not defined PY_CMD (
    where python3 >nul 2>&1 && set PY_CMD=python3
)

if not defined PY_CMD (
    echo [ERROR] Python interpreter tidak ditemukan di PATH.
    echo Pastikan Python 3.8+ telah terinstal.
    exit /b 1
)

echo Menjalankan unit tests menggunakan: %PY_CMD%
%PY_CMD% -m unittest discover -s tests -p "test_*.py" -v
exit /b %ERRORLEVEL%

