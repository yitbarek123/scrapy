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
    allowed_domains = ["www.binance.com"]
    start_urls = ["https://www.binance.com/en/trade/BTC_USDT"]

    def start_requests(self):
        ps=["BTCUSDT","ETHUSDT","ADAUSDT","XRPUSDT"]
        ps=["BTC_USDT"]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
            'Accept-Language': 'en-US,en;q=0.5',
            # Add other headers if needed
        }
        for p in ps:
            yield scrapy.Request("https://www.binance.com/en/trade/"+p,meta={'playwright':True,'headers': headers},cb_kwargs={'p': p})
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
            context = await browser.new_context(java_script_enabled=True,viewport={"width":1920, "height":1080},user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0")
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

            button_id = 'onetrust-accept-btn-handler'
            button_selector = f'button#{button_id}'
            await page.click(button_selector)

            await page.wait_for_timeout(10000)
            while True:
                
                xpath = '//div[@class="orderbook-list orderbook-ask has-overlay"]//div[@class="ask-light" or @class="text"]'
                elements_amount = await page.query_selector_all(xpath)
                #print(elements_amount)
                
                xpath2 = '//div[@class="orderbook-list orderbook-bid has-overlay"]//div[@class="bid-light" or @class="text"]'
                elements_amount2 = await page.query_selector_all(xpath2)
                #elements_amount += elements_amount2

                result_lists=[]
                cc=0
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    current_timestamp = int(time.time())
                    if ":" in text_contentt:
                        continue
                    result_lists.append(text_contentt.replace("\n","").replace(" ","").replace(",",""))
                    #result_lists.append("buy")
                    cc+=1
                    if cc==3:
                        result_lists.append(str(current_timestamp))
                        result_lists.append("buy")
                        cc=0
                cc=0
                result_lists2=[]
                for element in elements_amount2:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    current_timestamp = int(time.time())
                    if ":" in text_contentt:
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
                result_list_of_tuples1=[tuple(result_lists[i:i+5]) for i in range(0, len(result_lists), 5)]
                
                #result_list_of_tuples1 = min(result_list_of_tuples1, key=lambda x: x[0])
                
                result_list_of_tuples2=[tuple(result_lists2[i:i+5]) for i in range(0, len(result_lists2), 5)]
                #result_list_of_tuples2 = max(result_list_of_tuples2, key=lambda x: x[0])
                result_list_of_tuples = [result_list_of_tuples2] 
                result_list_of_tuples += [result_list_of_tuples1] 
                result_list_of_tuples1+=result_list_of_tuples2
                print(result_list_of_tuples1)
                time.sleep(0.25)
                url=p.replace("_","")#response.url[29:]
                litem['data']= result_list_of_tuples1
                litem['pair']= url.lower()
                yield litem
                #await page.wait_for_timeout(500)
        async with async_playwright() as pw:
            cnt2 = 0
            browser = await pw.firefox.launch(headless=False,)
            context = await browser.new_context(java_script_enabled=True,viewport={"width":1920, "height":1080})
            page = await context.new_page()
            print("###################")
            print("###################")
            print("URL: ",response.url)
            print("###################")
            print("###################")

            await page.goto(response.url)

            while True:
                time.sleep(100)