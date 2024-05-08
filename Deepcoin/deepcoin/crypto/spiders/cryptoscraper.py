import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
import asyncio
from crypto.items import CryptoItem
import os
class CryptoscraperSpider(scrapy.Spider):
    name = "cryptoscraper"
    allowed_domains = ["deepcoin.com"]
    start_urls = ["https://www.deepcoin.com/en/Spot?currentId=BTC%2FUSDT"]

    def start_requests(self):
        ps=["BTC%2FUSDT","ETH%2FUSDT","ADA%2FUSDT","XRP%2FUSDT"]
        ps=["BTC%2FUSDT"]

        for p in ps:
            yield scrapy.Request("https://www.deepcoin.com/en/Spot?currentId="+p,meta={'playwright':True},cb_kwargs={'p': p})
            print(ps)
            #time.sleep(100)


    async def parse5(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async for value in self.parse2(response):
            print(f"Received value: {value}")
            await asyncio.sleep(0.5)    
    
    async def parse(self, response,p):
        lock_file = '/shared_lock_files/'+str(response.url[43:].replace("%",""))+'.lock'
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
        #litem=CryptoItem()
        litem=CryptoItem()
        async with async_playwright() as pw:
            cnt = 0
            browser = await pw.firefox.launch(headless=True,)
            context = await browser.new_context(java_script_enabled=True,viewport={"width":1920, "height":1080})
            page = await context.new_page()
            print("###################")
            print("###################")
            print("URL: ",response.url)
            print("###################")
            print("###################")

            await page.goto(response.url)
            #print(page.content())
            #await page.wait_for_timeout(10000)
            #await browser.new_context(viewport={"width":1920, "height":1080})
            await page.wait_for_timeout(30000)
            xpath = '//div[@class="trades-header"]'
            elements_amount = await page.query_selector_all(xpath)
            print(elements_amount)
            #ime.sleep(100)
            pp= page.locator(f'//div[@class="trades-header"]//a[@class="tab"]')
            await pp.click()
            await page.wait_for_timeout(10000)
            while True:
                xpath = '//div[@class="market-list"]//div[@class="content"]//span'
                elements_amount = await page.query_selector_all(xpath)
                #print(elements_amount)
                result_lists=[]
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerHTML', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    if class_name == "_green":
                        #print(text_contentt)
                        result_lists.append("buy")
                    if class_name == "_red":
                        #print(text_contentt)
                        result_lists.append("sell")
                    result_lists.append(text_contentt.replace("\n","").replace(" ",""))
                    #print(class_name)
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
                time.sleep(0.3)
                url=response.url[43:].replace("%2F","")
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                yield litem
                #await page.wait_for_timeout(500)
            print("scrap again")
            yield scrapy.Request(response.url,meta={'playwright':True},callback=self.parse)