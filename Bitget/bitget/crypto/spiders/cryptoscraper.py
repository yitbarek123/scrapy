import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
import asyncio
from crypto.items import CryptoItem
from etcd import Client
import os

class CryptoscraperSpider(scrapy.Spider):
    name = "cryptoscraper"
    allowed_domains = ["bitget.com"]
    start_urls = ["https://www.bitget.com/spot/BTCUSDT"]
    etcd_client = Client(host='localhost', port=2379)

    def start_requests(self):
        lock_key = '/my_lock'
        lock_acquired = False
        ps=["BTCUSDT","ETHUSDT","ADAUSDT","XRPUSDT"]
        #ps=["BTCUSDT"]
        for p in ps:
            yield scrapy.Request("https://www.bitget.com/spot/"+p,meta={'playwright':True},cb_kwargs={'p': p})
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
            #print(page.content())
            #await page.wait_for_timeout(10000)
            #await browser.new_context(viewport={"width":1920, "height":1080})
            await page.wait_for_timeout(30000)
            pp= page.locator(f'//li[text()="Market trades"]')
            await pp.click()
            await page.wait_for_timeout(30000)
            result_list=[]
            old_result=[]
            cnt=0
            while True:
                xpath = '//body//li[@class="colored-text__fall text-left w-[30%]" or @class="colored-text__rise text-left w-[30%]" or @class="text-mainText w-[35%] text-right mr-2.5" or  @class="text-mainText w-[35%] text-right "]'
                elements_amount = await page.query_selector_all(xpath)
                #print(elements_amount)
                result_lists=[]
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    #result_lists.append(text_contentt)
                    if class_name == "colored-text__rise text-left w-[30%]":
                        #print("buy")
                        result_lists.append("buy")
                    if class_name == "colored-text__fall text-left w-[30%]":
                        #print("sell")
                        result_lists.append("sell")
                    #print(text_contentt)
                    result_lists.append(text_contentt)
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
                
                result_list_of_tuples=[tuple(result_lists[i:i+4]) for i in range(0, len(result_lists), 4)]
                #print(result_list_of_tuples)
                time.sleep(1)
                url=response.url[28:]
                litem['data']= result_list_of_tuples
                litem['pair']= url.lower()
                yield litem
                await page.wait_for_timeout(500)
            print("scrap again")
            yield scrapy.Request(response.url,meta={'playwright':True},callback=self.parse,cb_kwargs={'p': p})