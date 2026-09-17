@echo off
pushd "%~dp0system"
rem Level 7: multi-camera wall. Edit system\sources_config.py first.
rem LINE is off here. To send LINE: set LINE_TOKEN, then run  python monitor.py
python monitor.py --no-line
echo.
echo Done. Press any key to close.
pause >nul
popd
