@echo off
cd /d "%~dp0"

echo [1/3] Fetching market data...
python fetch_market_data.py
if %ERRORLEVEL% neq 0 (
    echo Error fetching data!
    pause
    exit /b 1
)

echo [2/3] Generating AI article...
python generate_articles.py
if %ERRORLEVEL% neq 0 (
    echo Error generating article!
    pause
    exit /b 1
)

echo [3/3] Uploading to GitHub and Vercel...
git add web-app/public/data/*
git commit -m "Auto-update market data and report: %date%"
git push origin main

echo All Done!
timeout /t 5
