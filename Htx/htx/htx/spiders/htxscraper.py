import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
import asyncio
from htx.items import HtxItem
from etcd import Client
import os

class HtxscraperSpider(scrapy.Spider):
    name = "htxscraper"
    allowed_domains = ["www.htx.com"]
    start_urls = ["https://www.htx.com/en-us/trade/btc_usdt"]

    def __init__(self, *args, **kwargs):
        super(HtxscraperSpider, self).__init__(*args, **kwargs)
        self.client = Client()
    def start_requests(self):
        urls=["https://www.htx.com/en-us/trade/btc_usdt","https://www.htx.com/en-us/trade/eth_usdt","https://www.htx.com/en-us/trade/ada_usdt","https://www.htx.com/en-us/trade/xrp_usdt"]        for url in urls:
            yield scrapy.Request(url,meta={'playwright':True})
    
    async def parse5(self, response):
        data = {}
        maxValue=0
        maxToken=""
        async for value in self.parse2(response):
            print(f"Received value: {value}")
            await asyncio.sleep(0.5)    
    
    async def parse(self, response):
        lock_file = '/shared_lock_files/'+str(response.url[26:].replace("_",""))+'.lock'
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
        async with async_playwright() as pw:
            cnt = 0
            browser = await pw.chromium.launch(headless=True,)
            context = await browser.new_context(viewport={"width":1920, "height":1080})
            page = await context.new_page()
            await page.goto(response.url)
            await page.wait_for_timeout(20000)
            pp= page.locator(f'//span[@class="trade-layout-group__tab"]')
            await pp.click()
            await page.wait_for_timeout(3000)
            result_list=[]
            old_result=[]
            litem=HtxItem()
            cnt=0
            while True:
                xpath = '//body//p[@class="trade-item"]//span'
                elements = await page.query_selector_all(xpath)
                result_list=[]
                for element in  elements:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    text_contentt2 = await page.evaluate('(element) => element.className', element)
                    result_list.append(text_contentt)
                    if text_contentt2=="price color-buy":
                        result_list.append("buy")
                    if text_contentt2=="price color-sell":
                        result_list.append("sell")
                if cnt==0:
                    old_result=result_list[0]
                if cnt>1200:
                    if result_list[0]==old_result:
                        os.remove(lock_file)
                        print("lock released")
                        break
                    old_result=result_list[0]
                    cnt=0
                if result_list==[]:
                    os.remove(lock_file)
                    print("lock released")
                    break
                cnt+=1
                print(cnt)
                result_list_of_tuples=[tuple(result_list[i:i+4]) for i in range(0, len(result_list), 4)]
                url = response.url[26:].replace("_","")
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                await page.wait_for_timeout(500)
                time.sleep(0.5)
                yield litem

            print("scrap again")
            yield scrapy.Request(response.url,meta={'playwright':True},callback=self.parse)