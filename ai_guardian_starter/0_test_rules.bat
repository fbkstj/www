@echo off
pushd "%~dp0system"
python test_rules.py
echo.
echo Done. Press any key to close.
pause >nul
popd
