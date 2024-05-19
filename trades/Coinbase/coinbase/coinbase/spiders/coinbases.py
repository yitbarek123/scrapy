import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
from coinbase.items import CoinbaseItem
import asyncio

class CoinbasescraperSpider(scrapy.Spider):
    name = "coinbasescraper"
    allowed_domains = ["exchange.coinbase.com"]
    start_urls = ["https://exchange.coinbase.com/trade/BTC-USD"]

    def start_requests(self):
        
        urls=["https://exchange.coinbase.com/trade/XRP-USD","https://exchange.coinbase.com/trade/BTC-USD","https://exchange.coinbase.com/trade/ETH-USD","https://exchange.coinbase.com/trade/ADA-USD"]
        urls=["https://exchange.coinbase.com/trade/BTC-USD"]#,"https://exchange.coinbase.com/trade/BTC-USD"]
        for url in urls:
            yield scrapy.Request(url,meta={'playwright':True})
            time.sleep(0.3)


    async def parse5(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async for value in self.parse2(response):
            print(f"Received value: {value}")
            await asyncio.sleep(0.5)    
    
    async def parse(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async with async_playwright() as pw:
            cnt = 0
            browser = await pw.firefox.launch(headless=False,)
            context = await browser.new_context(viewport={"width":1920, "height":1080})
            page = await context.new_page()
            await page.goto(response.url)
            #print(page.content())
            await page.wait_for_timeout(20000)
            
            cnt=0
            result_list_of_lists=[]
            litem=CoinbaseItem()
            while True:
                xpath = '//body//div[@class="OrderBookCanvas__HoverLayer-sc-1sy59bt-3 knHPeS"]'
                elements = await page.query_selector_all(xpath)
                
                xpath2 = '//body//div[@class="OrderBookCanvas__HoverLayer-sc-1sy59bt-3 knHPeS"]'
                elements2 = await page.query_selector_all(xpath2)
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
                    if cc==4:
                        result_lists.pop(-1)
                        result_lists.append(str(current_timestamp))
                        result_lists.append("buy")
                        cc=0
                print(result_lists)
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
                    if cc==4:
                        result_lists2.pop(-1)
                        result_lists2.append(str(current_timestamp))
                        result_lists2.append("sell")
                        cc=0
                    #print(class_name)
                print(result_lists)
                #await page.wait_for_timeout(50)
                time.sleep(0.1)





























