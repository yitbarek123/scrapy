import scrapy
from scrapy_playwright.page import PageMethod
from playwright.async_api import async_playwright
import json
from datetime import datetime
import time
import asyncio
from kucoin.items import KucoinItem

class KucoinscraperSpider(scrapy.Spider):
    name = "kucoinscraper"
    allowed_domains = ["www.kucoin.com"]
    start_urls = ["https://www.kucoin.com/trade/BTC-USDT"]

    def start_requests(self):
        urls = ["https://www.kucoin.com/trade/BTC-USDT","https://www.kucoin.com/trade/ETH-USDT","https://www.kucoin.com/trade/ADA-USDT","https://www.kucoin.com/trade/XRP-USDT"]
        urls = ["https://www.kucoin.com/trade/BTC-USDT"]
        for url in urls:
            yield scrapy.Request(url,meta={'playwright':True})
    
    async def parse(self, response):
        data = {}
        maxValue=0
        maxToken=""
        litem=KucoinItem()
        async with async_playwright() as pw:
            cnt = 0
            browser = await pw.firefox.launch(headless=False,)
            context = await browser.new_context(viewport={"width":1920, "height":1080})
            page = await context.new_page()
            await page.goto(response.url)
            #print(page.content())
            #await page.wait_for_timeout(10000)
            #await browser.new_context(viewport={"width":1920, "height":1080})
            await page.wait_for_timeout(60000)
            await page.wait_for_timeout(30000)
            while True:
                xpath = '//body//div[@class="orderbook-list-sell lrtcss-1xu4d3b"]//div[@class="lrtcss-123ghgt" or @class="lrtcss-1ltqx05" or @class="lrtcss-1k2ivai"]'
                xpath2 = '//body//div[@class="ReactVirtualized__Grid ReactVirtualized__List"]//div[@class="lrtcss-13dusx4" or @class="lrtcss-123ghgt" or @class="lrtcss-1tegiwn"]'
                
                elements_amount = await page.query_selector_all(xpath)
                elements_amount2 = await page.query_selector_all(xpath2)

                result_lists=[]
                cc=0
                for element in elements_amount:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    current_timestamp = int(time.time())

                    result_lists.append(text_contentt.replace("\n","").replace(" ","").replace(",",""))
                    #result_lists.append("buy")
                    cc+=1
                    if cc==3:
                        result_lists.append(str(current_timestamp))
                        result_lists.append("buy")
                        cc=0
                #print(result_lists)
                result_lists=result_lists[:20]
                cc=0
                result_lists2=[]
                for element in elements_amount2:
                    text_contentt = await page.evaluate('(element) => element.innerText', element)
                    class_name = await page.evaluate('(element) => element.className', element)
                    current_timestamp = int(time.time())
                    if text_contentt=='':
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
                print(result_lists2)
                result_lists2=result_lists2[:30]
                result_list_of_tuples1=[tuple(result_lists[i:i+5]) for i in range(0, len(result_lists), 5)]
                
                #result_list_of_tuples1 = min(result_list_of_tuples1, key=lambda x: x[0])
                
                result_list_of_tuples2=[tuple(result_lists2[i:i+5]) for i in range(0, len(result_lists2), 5)]
                #result_list_of_tuples2 = max(result_list_of_tuples2, key=lambda x: x[0])
                result_list_of_tuples = [result_list_of_tuples2] 
                result_list_of_tuples += [result_list_of_tuples1] 
                result_list_of_tuples1+=result_list_of_tuples2
                print(result_list_of_tuples1)
                time.sleep(0.25)
                url=response.url[29:].replace("-","")
                litem['data']= result_list_of_tuples1
                litem['pair']= url.lower()
                yield litem