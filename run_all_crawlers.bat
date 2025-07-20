@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo    Gaming Search Engine - Nightly Data Crawl
echo ========================================================
echo Start Time: %date% %time%
echo.

REM Set project paths
set PROJECT_DIR=D:\8th mid perp\gaming-search-engine
set CRAWLER_DIR=%PROJECT_DIR%\crawler
set LOG_DIR=%CRAWLER_DIR%\logs
set VENV_DIR=%PROJECT_DIR%\venv

REM Create logs directory if it doesn't exist
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM Set log file with timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"
set LOG_FILE=%LOG_DIR%\crawl_log_%timestamp%.txt

echo Logging to: %LOG_FILE%
echo.

REM Navigate to project directory
cd /d "%PROJECT_DIR%"

REM Check if virtual environment exists
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at %VENV_DIR%
    echo Please create virtual environment first: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating Python virtual environment...
call "%VENV_DIR%\Scripts\activate.bat" >> "%LOG_FILE%" 2>&1

REM Navigate to crawler directory
cd /d "%CRAWLER_DIR%"

REM Initialize counters
set SUCCESS_COUNT=0
set TOTAL_COUNT=4

echo --------------------------------------------------------
echo [1/4] Running IGN News Spider...
echo --------------------------------------------------------
scrapy crawl ign_news -O temp_ign.json >> "%LOG_FILE%" 2>&1
if exist "temp_ign.json" (
    python -c "
import json, os
try:
    # Load new data
    with open('temp_ign.json', 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    # Load existing data
    existing_data = []
    if os.path.exists('ign_news.json'):
        try:
            with open('ign_news.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except: pass
    
    # Filter duplicates and append
    existing_urls = {item.get('url', '') for item in existing_data}
    new_items = [item for item in new_data if item.get('url', '') not in existing_urls]
    combined_data = existing_data + new_items
    
    with open('ign_news.json', 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    os.remove('temp_ign.json')
    print(f'SUCCESS: IGN crawler completed, added {len(new_items)} new articles')
except Exception as e:
    print(f'ERROR: IGN crawler failed - {e}')
" >> "%LOG_FILE%" 2>&1
    set /a SUCCESS_COUNT+=1
    echo SUCCESS: IGN News Spider completed
) else (
    echo ERROR: IGN News Spider failed
)
echo.

echo --------------------------------------------------------
echo [2/4] Running Reddit Gaming Crawler...
echo --------------------------------------------------------
if exist "gaming_crawler\spiders\reddit_news.py" (
    python gaming_crawler\spiders\reddit_news.py >> "%LOG_FILE%" 2>&1
    if !errorlevel! equ 0 (
        set /a SUCCESS_COUNT+=1
        echo SUCCESS: Reddit Gaming Crawler completed
    ) else (
        echo ERROR: Reddit Gaming Crawler failed
    )
) else (
    echo WARNING: reddit_news.py not found, skipping...
)
echo.

echo --------------------------------------------------------
echo [3/4] Running WorkWithIndies Jobs Spider...
echo --------------------------------------------------------
scrapy crawl workwithindies_jobs -O temp_jobs.json >> "%LOG_FILE%" 2>&1
if exist "temp_jobs.json" (
    python -c "
import json, os
try:
    # Load new data
    with open('temp_jobs.json', 'r', encoding='utf-8') as f:
        new_data = json.load(f)
    
    # Load existing data
    existing_data = []
    if os.path.exists('workwithindies_jobs.json'):
        try:
            with open('workwithindies_jobs.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except: pass
    
    # Filter duplicates and append
    existing_urls = {item.get('url', '') for item in existing_data}
    new_items = [item for item in new_data if item.get('url', '') not in existing_urls]
    combined_data = existing_data + new_items
    
    with open('workwithindies_jobs.json', 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    os.remove('temp_jobs.json')
    print(f'SUCCESS: Jobs crawler completed, added {len(new_items)} new jobs')
except Exception as e:
    print(f'ERROR: Jobs crawler failed - {e}')
" >> "%LOG_FILE%" 2>&1
    set /a SUCCESS_COUNT+=1
    echo SUCCESS: WorkWithIndies Jobs Spider completed
) else (
    echo ERROR: WorkWithIndies Jobs Spider failed
)
echo.

echo --------------------------------------------------------
echo [4/4] Running General Deep Crawler...
echo --------------------------------------------------------
if exist "gaming_crawler\spiders\general_crawler.py" (
    python gaming_crawler\spiders\general_crawler.py >> "%LOG_FILE%" 2>&1
    if !errorlevel! equ 0 (
        set /a SUCCESS_COUNT+=1
        echo SUCCESS: General Deep Crawler completed
    ) else (
        echo ERROR: General Deep Crawler failed
    )
) else (
    echo WARNING: general_crawler.py not found, skipping...
)
echo.

REM Deactivate virtual environment
call deactivate >> "%LOG_FILE%" 2>&1

echo ========================================================
echo           Nightly Data Crawl Summary
echo ========================================================
echo End Time: %date% %time%
echo Successful Crawlers: %SUCCESS_COUNT%/%TOTAL_COUNT%
echo Log File: %LOG_FILE%
echo.

REM Generate summary report
echo Creating summary report...
python -c "
import json, os, glob
from datetime import datetime

summary = {
    'crawl_date': datetime.now().isoformat(),
    'successful_crawlers': %SUCCESS_COUNT%,
    'total_crawlers': %TOTAL_COUNT%,
    'files_status': {}
}

# Check JSON files (removed steam_news.json)
json_files = ['ign_news.json', 'reddit_news.json', 'workwithindies_jobs.json', 'gaming_content_crawl.json']
for file in json_files:
    if os.path.exists(file):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            summary['files_status'][file] = {
                'exists': True,
                'items_count': len(data) if isinstance(data, list) else len(data.get('pages', [])),
                'size_mb': round(os.path.getsize(file) / 1024 / 1024, 2)
            }
        except:
            summary['files_status'][file] = {'exists': True, 'error': 'Could not parse JSON'}
    else:
        summary['files_status'][file] = {'exists': False}

# Save summary
if not os.path.exists('logs'):
    os.makedirs('logs')
with open('logs/last_crawl_summary.json', 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print('Summary report saved to logs/last_crawl_summary.json')
" >> "%LOG_FILE%" 2>&1

if %SUCCESS_COUNT% equ %TOTAL_COUNT% (
    echo ✅ ALL CRAWLERS COMPLETED SUCCESSFULLY!
) else (
    echo ⚠️  Some crawlers failed. Check log file for details.
)

echo ========================================================
pause
