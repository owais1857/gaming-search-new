import scrapy
import time
import undetected_chromedriver as uc
from parsel import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse

class GameFAQsGuidesSpider(scrapy.Spider):
    name = "gamefaqs_guides"

    async def start(self):
        options = uc.ChromeOptions()
        # options.add_argument('--headless') 
        driver = uc.Chrome(options=options)

        # The URL is correct, but it needs a real browser to handle the redirect
        url = "https://gamefaqs.gamespot.com/faqs/new"
        driver.get(url)

        try:
            # Wait for the main content div, which we know is correct
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'main_content'))
            )
            print("--- Main content detected. ---")
            
            page_source = driver.page_source
            response = HtmlResponse(url=driver.current_url, body=page_source, encoding='utf-8')
            
            for guide in self.parse_guides(response):
                yield guide

        except Exception as e:
            print(f"AN ERROR OCCURRED while scraping GameFAQs: {e}")
        finally:
            driver.quit()

    def parse_guides(self, response):
        # The selectors for the table are correct
        for row in response.css("table.results tbody tr"):
            guide_title = row.css("td.c_title a::text").get()
            if guide_title:
                yield {
                    "guide_title": guide_title.strip(),
                    "game_name": row.css("td.c_game a::text").get(),
                    "platform": row.css("td.c_plat::text").get(),
                    "author": row.css("td.c_author a::text").get(),
                    "url": response.urljoin(row.css("td.c_title a::attr(href)").get()),
                    "source": "GameFAQs"
                }