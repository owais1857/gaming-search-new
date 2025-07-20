@echo off
cd "D:\8th mid perp\gaming-search-engine\crawler"
call ..\venv\Scripts\activate
echo "Starting jobs crawler (append mode)..."
scrapy crawl workwithindies_jobs -o workwithindies_jobs.json -s FEED_OVERWRITE=False
deactivate