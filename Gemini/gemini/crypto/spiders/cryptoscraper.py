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
    allowed_domains = ["gemini.com"]
    start_urls = ["https://www.bitmart.com/trade/en-US?layout=pro&theme=dark&symbol=BTC_USDT"]

    def start_requests(self):
        ps=["BTCUSDT","ETHUSDT","ADAUSDT","XRPUSDT"]
        ps=["BTCUSDT"]
        for p in ps:
            yield scrapy.Request("https://exchange.gemini.com/trade/"+p,meta={'playwright':True})
            print(p)
            #time.sleep(100)


    async def parse5(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async for value in self.parse2(response):
            print(f"Received value: {value}")
            await asyncio.sleep(0.5)    
    
    async def parse(self, response):
        lock_file = '/shared_lock_files/'+str(response.url[34:].replace("/",""))+'.lock'
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
            print(response.url)
            print("###################")
            print("###################")

            await page.goto(response.url)

            await page.wait_for_timeout(30000)
            while True:
                temp=0
                # item-col price buy
                xpath = '//body//span[@class="css-7ozuhk e1bj5tt54" or @class="css-1yd3h3m e1bj5tt52" or @class="css-1h7ji1b e1bj5tt52" or @class="css-ac3ro5 e1bj5tt53"]'
                #xpath = '//body//li[@class="list-item"]//span'
                

                elements_amount = await page.query_selector_all(xpath)
                #print(elements_amount)
                result_lists=[]
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    direction_name = await page.evaluate('(element) => element.getAttribute("direction")', element)
                    #print(direction_name)
                    if direction_name == "1":
                        #print("buy")
                        result_lists.append("buy")
                        #result_lists.append(text_contentt)
                    if direction_name == "-1":
                        #print("sell")
                        result_lists.append("sell")
                    result_lists.append(text_contentt)
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

                url=response.url[34:]
                url = url.replace("_","")
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                yield litem
                time.sleep(0.5)
            print("scrap again")
            yield scrapy.Request(response.url,meta={'playwright':True},callback=self.parse)
