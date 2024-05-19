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
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'RETRY_TIMES': 3,  
    }
    def __init__(self, *args, **kwargs):
        super(HtxscraperSpider, self).__init__(*args, **kwargs)
        self.client = Client()
    def start_requests(self):
        urls=["https://www.htx.com/en-us/trade/btc_usdt","https://www.htx.com/en-us/trade/eth_usdt","https://www.htx.com/en-us/trade/ada_usdt","https://www.htx.com/en-us/trade/xrp_usdt"]
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
        lock_file = '/shared_lock_files/'+str(response.url[26:].replace("-",""))+'.lock'
        # Attempt to acquire the lock
        cnt2=0
        while os.path.exists(lock_file):
            print("Lock file exists. Waiting to acquire the lock...")
            if cnt2>71800:
                os.remove(lock_file)
                cnt2=0
            cnt2+=1
            time.sleep(0.5)
        # Create the lock file
        with open(lock_file, 'w') as f:
            f.write('Lock acquired') 
            print("file created")  
        print("file created")        
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
            old_result=""
            litem=HtxItem()
            cnt=1
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
                result_lists=result_list
                print(result_lists)
                if old_result=="":
                    if len(result_lists)>0:
                        old_result=result_lists[0]
                if cnt%1200==0:
                    if old_result==result_lists[0]:
                        try:
                            os.remove(lock_file)
                        except:
                            pass
                        print("lock released")
                        cnt=1
                        break
                    old_result=result_lists[0]
                if cnt>72000:
                    #if result_lists[0]==old_result:
                    #os.remove(lock_file)
                    print("lock released")
                    cnt=1
                    break
                if cnt>1500:
                    if result_lists==[]:
                        os.remove(lock_file)
                        print("lock released")
                        cnt=1
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