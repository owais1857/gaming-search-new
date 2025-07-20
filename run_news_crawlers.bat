@echo off
cd "D:\8th mid perp\gaming-search-engine\crawler"
call ..\venv\Scripts\activate
echo "Starting news crawlers (append mode)..."
scrapy crawl ign_news -o ign_news_deep.json -s FEED_OVERWRITE=False
python reddit_news.py
deactivate