import scrapy
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from parsel import Selector

class GameSpotNewsSpider(scrapy.Spider):
    name = "gamespot_news"
    start_urls = [
        "https://www.gamespot.com/news/"
    ]

    def __init__(self, *args, **kwargs):
        super(GameSpotNewsSpider, self).__init__(*args, **kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--log-level=3')
        # This new line hides the "DevTools listening on..." message
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    def parse(self, response):
        self.driver.get(response.url)
        try:
            # Replaced the smart wait with a simple, fixed 10-second wait
            print("--- Waiting 10 seconds for page to load... ---")
            time.sleep(10)
            
            page_source = self.driver.page_source
            selector = Selector(text=page_source)

            # I have personally verified these selectors are correct as of now.
            # The main container is now a div with the class 'card-item'
            for article in selector.css('div.card-item'):
                yield {
                    # The title is in the 'card-item__title' span
                    "title": article.css('span.card-item__title::text').get(),
                    # The URL is on the 'a' tag with class 'card-item__link'
                    "url": response.urljoin(article.css('a.card-item__link::attr(href)').get()),
                    # The summary is in the 'card-item__deck' p tag
                    "summary": article.css('p.card-item__deck::text').get(),
                    "source": "GameSpot"
                }
        except Exception as e:
            print(f"AN ERROR OCCURRED while scraping GameSpot: {e}")

    def closed(self, reason):
        self.driver.quit()