import scrapy
import time
import undetected_chromedriver as uc
from parsel import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.http import HtmlResponse

class GamedevJobsSpider(scrapy.Spider):
    name = "gamedev_jobs"

    async def start(self):
        options = uc.ChromeOptions()
        # By commenting out the line below, we tell Selenium to open a visible browser window
        # options.add_argument('--headless') 
        driver = uc.Chrome(options=options)

        url = "https://gamedev.jobs/"
        driver.get(url)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, 'job-list-container'))
            )
            print("--- Main content detected. ---")
            
            # Give a moment for the page to settle
            time.sleep(3)
            
            page_source = driver.page_source
            response = HtmlResponse(url=driver.current_url, body=page_source, encoding='utf-8')
            
            for job in self.parse_jobs(response):
                yield job

        except Exception as e:
            print(f"AN ERROR OCCURRED while scraping Gamedev.jobs: {e}")
        finally:
            print("--- Spider finished, browser will close shortly. ---")
            time.sleep(5) # Keep the browser open for 5 seconds to see the result
            driver.quit()

    def parse_jobs(self, response):
        for job in response.css("div.job-tile"):
            yield {
                "job_title": job.css("a.job-title::text").get(),
                "company": job.css("a.company-name::text").get(),
                "location": job.css("div.location::text").get(),
                "url": response.urljoin(job.css("a.job-title::attr(href)").get()),
                "source": "Gamedev.jobs"
            }