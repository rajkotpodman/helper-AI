@echo off
title Playwright CRM Codegen Recorder - Helper-AI
cls
echo ===================================================================
echo     Helper-AI • Microsoft Playwright CRM Codegen Recorder
echo ===================================================================
echo.
echo This tool opens Google Chrome and records your clicks and typing live.
echo As you fill out any CRM form, Playwright writes the automation code!
echo.
set /p TARGET_URL="Enter Portal or CRM URL (Press Enter for default): "
if "%TARGET_URL%"=="" set TARGET_URL=https://google.com

echo.
echo Launching Playwright Inspector with Chrome...
echo Output script will be saved in: workflows\playwright\recorded_workflow.py
echo.
python -m playwright codegen --channel chrome -o "workflows\playwright\recorded_workflow.py" "%TARGET_URL%"
echo.
echo Recording finished! Script saved to workflows\playwright\recorded_workflow.py
pause
