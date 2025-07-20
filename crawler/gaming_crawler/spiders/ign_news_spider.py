import scrapy
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from parsel import Selector

# Imports for smart waiting
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class IGNNewsSpider(scrapy.Spider):
    name = "ign_news"
    start_urls = [
        "https://www.ign.com/news"
    ]

    def __init__(self, *args, **kwargs):
        super(IGNNewsSpider, self).__init__(*args, **kwargs)
        # Setup Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--log-level=3')
        # This line prevents the "DevTools listening on..." message
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    def parse(self, response):
        print("--- Fetching page with Selenium to load JavaScript ---")
        self.driver.get(response.url)
        
        try:
            # Smart Wait: Wait up to 20 seconds for the main content container to be visible
            # We are waiting for an element with the 'data-cy' attribute 'main-content'
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'section[data-cy="main-content"]'))
            )
            print("--- Main content detected. ---")

            # Try to find and click the cookie consent button if it exists
            try:
                cookie_button = self.driver.find_element(By.ID, 'onetrust-accept-btn-handler')
                cookie_button.click()
                print("--- Clicked cookie consent button. ---")
                time.sleep(2) # Give it a moment to disappear
            except:
                print("--- No cookie button found, continuing. ---")

            # Get the page source after everything has loaded
            page_source = self.driver.page_source
            
            # Use Scrapy's Selector on the final page source
            selector = Selector(text=page_source)

            print("--- Scraping content from the fully loaded page ---")
            
            # I've updated the selector to be more specific and reliable
            for article in selector.css('div[data-cy="content-item"]'):
                yield {
                    # This selector targets the title specifically
                    "title": article.css('span[data-cy="item-title"]::text').get(),
                    # The URL is on the parent link of the main item body
                    "url": response.urljoin(article.css('a[data-cy="item-body"]::attr(href)').get()),
                    # The summary is now called a subtitle
                    "summary": article.css('div[data-cy="item-subtitle"]::text').get(),
                    "source": "IGN"
                }
        except Exception as e:
            print(f"AN ERROR OCCURRED: {e}")
        
    def closed(self, reason):
        # Close the browser when the spider is done
        self.driver.quit()
        print("--- Selenium WebDriver closed ---")