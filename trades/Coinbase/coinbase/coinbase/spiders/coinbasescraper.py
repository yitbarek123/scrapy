import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
from coinbase.items import CoinbaseItem
import asyncio
import os

class CoinbasescraperSpider(scrapy.Spider):
    name = "coinbasescraper"
    allowed_domains = ["exchange.coinbase.com"]
    start_urls = ["https://exchange.coinbase.com/trade/BTC-USD"]

    def start_requests(self):
        
        urls=["https://exchange.coinbase.com/trade/XRP-USD","https://exchange.coinbase.com/trade/BTC-USD","https://exchange.coinbase.com/trade/ETH-USD","https://exchange.coinbase.com/trade/ADA-USD"]
        urls=["https://exchange.coinbase.com/trade/BTC-USDT"]#,"https://exchange.coinbase.com/trade/BTC-USD"]
        for url in urls:
            yield scrapy.Request(url,meta={'playwright':True})
            #time.sleep(100)


    async def parse5(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async for value in self.parse2(response):
            print(f"Received value: {value}")
            await asyncio.sleep(0.5)    
    
    async def parse(self, response):
        lock_file = '/shared_lock_files/'+str(response.url[65:].replace("_",""))+'.lock'
        while os.path.exists(lock_file):
            print("Lock file exists. Waiting to acquire the lock...")
            time.sleep(1)
        # Create the lock file
        with open(lock_file, 'w') as f:
            f.write('Lock acquired')  
        data = {}
        maxValue=0
        maxToken=""
        async with async_playwright() as pw:
            cnt = 0
            browser = await pw.firefox.launch(headless=True,)
            context = await browser.new_context(viewport={"width":1920, "height":1080})
            page = await context.new_page()
            await page.goto(response.url)
            #print(page.content())
            await page.wait_for_timeout(20000)
            
            cnt=0
            result_list_of_lists=[]
            litem=CoinbaseItem()
            while True:
                xpath = '//body//div[@class="TradeHistory__TradeHistoryContainer-sc-5ymjru-0 fDLmiH"]//span'
                elements = await page.query_selector_all(xpath)
                
                result_lists=[]
                element1=""
                for element in elements:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    style_name = await page.evaluate('(element) => element.getAttribute("style")', element)
                    current_timestamp = int(time.time())
                    if text_contentt=="":
                        continue
                    if ":" in text_contentt and result_lists[-1] !=text_contentt.replace("\n","").replace(" ","").replace(",",""):
                        result_lists.append(text_contentt.replace("\n","").replace(" ","").replace(",",""))
                        continue
                    if "."==text_contentt.replace("\n","").replace(" ","").replace(",","")[-1]:
                        element1=text_contentt.replace("\n","").replace(" ","").replace(",","")
                        continue
                    if element1!="":
                        result_lists.append(element1+text_contentt.replace("\n","").replace(" ","").replace(",",""))
                        element1=""
                    if "39" in style_name:
                        result_lists.append("buy")
                    if "240" in style_name:
                        result_lists.append("sell")
                    #result_lists.append("buy")
                #await page.wait_for_timeout(50)
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
                url = response.url[36:].replace("-","")
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                await page.wait_for_timeout(500)
                time.sleep(0.5)
                yield litem
                time.sleep(0.1)
            print("scrap again")
            yield scrapy.Request(response.url,meta={'playwright':True},callback=self.parse)




























