@echo off
echo ========================================================
echo Gaming Search Engine - Setup Checker
echo ========================================================

set PROJECT_DIR=D:\8th mid perp\gaming-search-engine
cd /d "%PROJECT_DIR%"

echo [1] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo ✅ Virtual environment found
) else (
    echo ❌ Virtual environment missing
    echo Run: python -m venv venv
    echo Then: pip install scrapy requests beautifulsoup4
)

echo.
echo [2] Checking Scrapy spiders...
cd crawler
if exist "..\venv\Scripts\activate.bat" (
    call ..\venv\Scripts\activate.bat
    scrapy list 2>nul
    call deactivate
) else (
    echo Cannot check spiders - virtual environment missing
)

echo.
echo [3] Checking Python crawler files...
cd gaming_crawler\spiders
if exist "general_crawler.py" (
    echo ✅ general_crawler.py found
) else (
    echo ❌ general_crawler.py missing
)

if exist "reddit_news.py" (
    echo ✅ reddit_news.py found  
) else (
    echo ❌ reddit_news.py missing
)

echo.
echo [4] Checking existing JSON files...
cd ..\..\
echo JSON files in crawler directory:
dir *.json /b 2>nul

echo.
echo ========================================================
echo Setup check complete
echo ========================================================
pause
