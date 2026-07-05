@echo off
python -m playwright install chromium
playwright codegen https://ads.google.com/aw/campaigns/new
pause
