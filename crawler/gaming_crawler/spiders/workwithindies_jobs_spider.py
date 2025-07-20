import scrapy
import time
import undetected_chromedriver as uc
from parsel import Selector
from selenium.webdriver.common.by import By
from scrapy.http import HtmlResponse

class WorkWithIndiesJobsSpider(scrapy.Spider):
    name = "workwithindies_jobs"

    async def start(self):
        options = uc.ChromeOptions()
        # You can add this back in to hide the browser window
        # options.add_argument('--headless') 
        driver = uc.Chrome(options=options)

        url = "https://www.workwithindies.com/"
        driver.get(url)

        try:
            # We will use a simple, reliable sleep since waiting for elements was tricky
            print("--- Waiting 10 seconds for page to load... ---")
            time.sleep(10)
            
            page_source = driver.page_source
            response = HtmlResponse(url=driver.current_url, body=page_source, encoding='utf-8')
            
            for job in self.parse_jobs(response):
                yield job

        except Exception as e:
            print(f"AN ERROR OCCURRED while scraping WorkWithIndies: {e}")
        finally:
            driver.quit()

    def parse_jobs(self, response):
        # *** THESE ARE THE CORRECT SELECTORS BASED ON YOUR HTML FILE ***
        # The main container for each job is an 'a' tag with the class 'job-card'
        for job in response.css('a.job-card'):
            
            # The company and location are both in bold divs, we get them all
            bold_texts = job.css('div.job-card-text.bold::text').getall()
            company = bold_texts[0] if bold_texts else None
            location = bold_texts[-1] if bold_texts else None

            yield {
                # The title is in a div with class 'text-block-28'
                'job_title': job.css('div.text-block-28::text').get(),
                'company': company,
                'location': location,
                # The URL is the href attribute of the main 'a' tag
                'url': response.urljoin(job.css('::attr(href)').get()),
                'source': "WorkWithIndies"
            }