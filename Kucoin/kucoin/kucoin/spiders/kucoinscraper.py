import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
import asyncio
from kucoin.items import KucoinItem
import os
class KucoinscraperSpider(scrapy.Spider):
    name = "kucoinscraper"
    allowed_domains = ["www.kucoin.com"]
    start_urls = ["https://www.kucoin.com/trade/BTC-USDT"]

    def start_requests(self):
        urls = ["https://www.kucoin.com/trade/BTC-USDT"]#,"https://www.kucoin.com/trade/ETH-USDT","https://www.kucoin.com/trade/ADA-USDT","https://www.kucoin.com/trade/XRP-USDT"]
        for url in urls:
            yield scrapy.Request(url,meta={'playwright':True})
            #time.sleep(100)
    async def parse(self, response):
        lock_file = '/shared_lock_files/'+str(response.url[29:].replace("-",""))+'.lock'
        # Attempt to acquire the lock
        while os.path.exists(lock_file):
            print("Lock file exists. Waiting to acquire the lock...")
            time.sleep(1)
        # Create the lock file
        with open(lock_file, 'w') as f:
            f.write('Lock acquired')   
        data = {}
        maxValue=0
        maxToken=""
        litem=KucoinItem()
        async with async_playwright() as pw:
            cnt = 0
            browser = await pw.chromium.launch(headless=True,)
            context = await browser.new_context(viewport={"width":1920, "height":1080})
            page = await context.new_page()
            await page.goto(response.url)
            #print(page.content())
            #await page.wait_for_timeout(10000)
            #await browser.new_context(viewport={"width":1920, "height":1080})
            await page.wait_for_timeout(60000)
            xpath = '//div[@class="flexlayout__tab_button_content" and text()="Recent Trades"]'
            elements = await page.query_selector_all(xpath)
            print(elements)
            pp= page.locator(f'//div[@class="flexlayout__tab_button_content" and text()="Recent Trades"]')
            await pp.click()
            await page.wait_for_timeout(30000)
            while True:
                xpath = '//body//div[@class="recent-buy" or @class="recent-sell" or @class="recent-time" or @class="recent-price" or @class="recent-amount"]'
                elements_amount = await page.query_selector_all(xpath)
                result_lists=[]
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    result_lists.append(text_contentt)
                    if class_name=='recent-buy':
                        #print("buy")
                        result_lists.append("buy")
                    if class_name=='recent-sell':
                        #print("sell")
                        result_lists.append("sell")
                        #self.log(f"Class name: {class_name}")
                if cnt==0:
                    old_result=result_lists[0]
                if cnt>1200:
                    if result_lists[0]==old_result:
                        os.remove(lock_file)
                        print("lock released")
                        break
                    old_result=result_lists[0]
                    cnt=0
                if result_lists==[]:
                    os.remove(lock_file)
                    print("lock released")
                    break
                cnt+=1
                print(cnt)
                
                result_list_of_tuples=[tuple(result_lists[i:i+4]) for i in range(0, len(result_lists), 4)]
                print(result_list_of_tuples)
                url=response.url[29:].replace("-","")
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                yield litem
                await page.wait_for_timeout(500)
                time.sleep(0.5)
            print("scrap again")
            yield scrapy.Request(response.url,meta={'playwright':True},callback=self.parse)