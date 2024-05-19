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
        
        url="https://exchange.coinbase.com/trade/BTC-USD"
        yield scrapy.Request(url,meta={'playwright':True})
        url="https://exchange.coinbase.com/trade/ETH-USD"
        yield scrapy.Request(url,meta={'playwright':True})

    async def parse(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async for value in self.parse2(response):
            print(f"Received value: {value}")
            await asyncio.sleep(0.5)    
    
    async def parse2(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async with async_playwright() as pw:
            cnt = 0
            browser = await pw.chromium.launch(headless=False,)
            context = await browser.new_context(viewport={"width":1920, "height":1080})
            page = await context.new_page()
            await page.goto("https://exchange.coinbase.com/trade/BTC-USD")
            #print(page.content())
            await page.wait_for_timeout(20000)
            
            cnt=0
            result_list_of_lists=[]
            litem=CoinbaseItem()
            while True:
                xpath = '//body//div[@class="Scroller__StyledScroller-sc-1fpd2wx-2 bsziRM"]'
                elements = await page.query_selector_all(xpath)
                #for element in elements:
                # Use page.evaluate to get the text content of each matching element
                for element in  elements:
                    text_content = await page.evaluate('(element) => element.innerText', element)
                    original_list=text_content.split('\n')
                    #result_list_of_lists = [original_list[i:i+3] for i in range(0, len(original_list), 3)]
                    #yield result_list_of_lists
                    #if len(original_list) > 15:
                    #    result_list_of_lists+=[tuple(original_list[i:i+3]) for i in range(0, len(original_list), 3)]
                    #    cnt+=1
                    #if cnt>10:        
                    #        cnt=0
                    #        result_list_of_lists=list(set(result_list_of_lists))
                    #        litem['data']= result_list_of_lists
                    #        #item = {
                    #        #    'data': result_list_of_lists
                    #        #}
                    result_list_of_lists = [tuple(original_list[i:i+3]) for i in range(0, len(original_list), 3)]
                    #print(result_list_of_lists)
                    litem['data']= result_list_of_lists
                    #litem = {
                    #        'data': result_list_of_lists
                    #        }
                    yield litem
                await page.wait_for_timeout(500)
                time.sleep(0.5)
