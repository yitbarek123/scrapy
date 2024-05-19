import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
import asyncio
from crypto.items import CryptoItem

class CryptoscraperSpider(scrapy.Spider):
    name = "cryptoscraper"
    allowed_domains = ["mexc.com"]
    start_urls = ["https://www.mexc.com/exchange/BTC_USDT"]

    def start_requests(self):
        ps=["BTC_USDT","ADA_USDT","ETH_USDT","XRP_USDT"]
        ps=["BTC_USDT"]
        for p in ps:
            yield scrapy.Request("https://www.mexc.com/exchange/"+p,meta={'playwright':True},cb_kwargs={'p': p})
            print(ps)


    async def parse5(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async for value in self.parse2(response):
            print(f"Received value: {value}")
            await asyncio.sleep(0.5)    
    
    async def parse(self, response,p):
        data = {}
        maxValue=0
        maxToken=""
        #litem=CryptoItem()
        litem=CryptoItem()
        async with async_playwright() as pw:
            cnt = 0
            browser = await pw.firefox.launch(headless=False,)
            context = await browser.new_context(java_script_enabled=True,viewport={"width":1920, "height":1080})
            page = await context.new_page()
            print("###################")
            print("###################")
            print(response.url)
            print("###################")
            print("###################")

            await page.goto(response.url)
            #print(page.content())
            #await page.wait_for_timeout(10000)
            #await browser.new_context(viewport={"width":1920, "height":1080})
            await page.wait_for_timeout(30000)
            while True:
                xpath = '//body//div[@class="orderbook_price__cuGtY orderbook_sell__O8E9Q" or @class="orderbook_vol__z1Ryy" or @class="orderbook_amount__nZxFj"]'
                xpath2 = '//body//div[@class="orderbook_price__cuGtY orderbook_sell__O8E9Q" or @class="orderbook_vol__z1Ryy" or @class="orderbook_amount__nZxFj"]'
                elements_amount = await page.query_selector_all(xpath)
                elements_amount2 = await page.query_selector_all(xpath2)

                result_lists=[]
                cc=0
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    current_timestamp = int(time.time())
                    if text_contentt=="":
                        continue
                    result_lists.append(text_contentt.replace("\n","").replace(" ","").replace(",",""))
                    #result_lists.append("buy")
                    cc+=1
                    if cc==3:
                        result_lists.append(str(current_timestamp))
                        result_lists.append("buy")
                        cc=0
                
                result_lists=result_lists[:20]
                cc=0
                result_lists2=[]
                for element in elements_amount2:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    current_timestamp = int(time.time())
                    if text_contentt=="":
                        continue
                    
                    result_lists2.append(text_contentt.replace("\n","").replace(" ","").replace(",",""))
                    #result_lists.append("sell")
                    #result_lists2.append(str(current_timestamp))
                    cc+=1
                    if cc==3:
                        result_lists2.append(str(current_timestamp))
                        result_lists2.append("sell")
                        cc=0
                    #print(class_name)
                print(result_lists)
                result_lists2=result_lists2[:20]
                result_list_of_tuples1=[tuple(result_lists[i:i+5]) for i in range(0, len(result_lists), 5)]
                
                #result_list_of_tuples1 = min(result_list_of_tuples1, key=lambda x: x[0])
                
                result_list_of_tuples2=[tuple(result_lists2[i:i+5]) for i in range(0, len(result_lists2), 5)]
                #result_list_of_tuples2 = max(result_list_of_tuples2, key=lambda x: x[0])
                result_list_of_tuples = [result_list_of_tuples2] 
                result_list_of_tuples += [result_list_of_tuples1] 
                result_list_of_tuples1 += result_list_of_tuples2
                print(result_list_of_tuples1)
                time.sleep(0.25)
                url=p.replace("_","")
                litem['data']= result_list_of_tuples1
                litem['pair']= url.lower()
                yield litem