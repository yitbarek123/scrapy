import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
import asyncio
from crypto.items import CryptoItem

class CryptoscraperSpider(scrapy.Spider):
    name = "lbankscraper"
    allowed_domains = ["lbank.com"]
    start_urls = ["https://www.lbank.com/trade/btc_usdt"]

    def start_requests(self):
        ps=["BTC_USDT","ETH_USDT","ADA_USDT"]
        ps=["btc_usdt","eth_usdt","ada_usdt","xrp_usdt"]
        for p in ps:
            yield scrapy.Request("https://www.lbank.com/trade/"+p,meta={'playwright':True},cb_kwargs={'p': p})
            print(ps)
            time.sleep(100)


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
            browser = await pw.firefox.launch(headless=True)
            context = await browser.new_context(java_script_enabled=True,viewport={"width":1920, "height":1080})
            page = await context.new_page()
            print("###################")
            print("###################")
            print(response.url)
            print("###################")
            print("###################")

            await page.goto("https://www.lbank.com/trade/"+p)
            #print(page.content())
            #await page.wait_for_timeout(10000)
            #await browser.new_context(viewport={"width":1920, "height":1080})
            await page.wait_for_timeout(30000)
            while True:
                xpath = '//div[@class="index_right__i2mE0"]//ul[@class="index_ul__qih3J"]//div[@class="index_tradeTableItem__L6Z9U"]//span'
                elements_amount = await page.query_selector_all(xpath)
                #print(elements_amount)
                result_lists=[]
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.getAttribute("style")', element)
                    #result_lists.append(text_contentt)
                    if "209" in class_name:
                        print("buy")
                        result_lists.append("buy")
                    if "49" in class_name:
                        print("sell")
                        result_lists.append("sell")
                    print(text_contentt)
                    result_lists.append(text_contentt)
                    #l=text_contentt.split("\n")
                    
                    #if len(l)==3:
                    #    for i in range(3):
                    #        result_lists.append(l[i])
                result_list_of_tuples=[tuple(result_lists[i:i+4]) for i in range(0, len(result_lists), 4)]
                print(result_list_of_tuples)
                url=p.replace("_","")
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                yield litem
                #await page.wait_for_timeout(1000)
                time.sleep(0.2)