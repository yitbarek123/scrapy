import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
import asyncio
from crypto.items import CryptoItem

class CryptoscraperSpider(scrapy.Spider):
    name = "htxscraper"
    allowed_domains = ["www.htx.com"]
    start_urls = ["https://www.htx.com/en-us/trade/btc_usdt"]

    def start_requests(self):
        urls=["https://crypto.com/exchange/trade/BTC_USD"]
        for url in urls:
            yield scrapy.Request(url,meta={'playwright':True})


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
        #litem=CryptoItem()
        async with async_playwright() as pw:
            cnt = 0
            browser = await pw.chromium.launch(headless=False,)
            context = await browser.new_context(viewport={"width":1920, "height":1080})
            page = await context.new_page()
            await page.goto(response.url)
            #print(page.content())
            #await page.wait_for_timeout(10000)
            #await browser.new_context(viewport={"width":1920, "height":1080})
            await page.wait_for_timeout(30000)
            xpath = '//body//div[@class="list-item pointer SELL" or @class="list-item pointer BUY"]'
            elements_amount = await page.query_selector_all(xpath)
            print(elements_amount)