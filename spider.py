import scrapy ,csv
from scrapy.http import Request
from scrapy.crawler import CrawlerProcess
import re
import csv

keylist = ['誠齋','義齋','新齋（1-2樓）','新齋（3-4樓）','新齋（5-6樓）','新齋（7-8樓）','鴻齋1','鴻齋2','禮齋','仁齋','實齋','信A齋','信B齋','信C齋','善齋','碩齋1','碩齋2','華齋','明齋','平齋','文齋','靜齋','雅齋','慧齋','學齋AB','學齋CD','儒齋AB','儒齋CD','清齋A','清齋B','清齋C','清齋D','清齋E']
dorms = {}
for i in keylist:
    dorms[i] = None

class GetDataSpider(scrapy.Spider):
    name = 'getdata'
    start_urls = [
        'https://net.nthu.edu.tw/netsys/network:traffic:abtraff',
    ]

    def parse(self, response):
        for building in response.css('div.li > a'):
            info = {}
            info['name'] = building.css('::text').extract()
            link = building.css("::attr('href')").extract()
            yield Request(url=link[0], callback=self.parse2, meta={'info': info})

    def parse2(self, response):
        info = response.meta['info']
        indata = response.css("tr.in > td::text").extract()[0:2]
        outdata = response.css("tr.out > td::text").extract()[0:2]
        number = []
        #special case, might be kb
        change_unit1 = 1
        change_unit2 = 1
        if ('kb/秒' in indata[0]):
            change_unit1 = 1000
        if ('kb/秒' in outdata[0]):
            change_unit2 = 1000

        for string in indata:
            number.extend(re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", string))
        for string in outdata:
            number.extend(re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", string))
        global dorms
        dorms[info['name'][-1].strip()] = [float(number[0])/change_unit1, float(number[4])/change_unit2, float(number[1]), float(number[5]), float(number[3]), float(number[7])]

c = CrawlerProcess({})
c.crawl(GetDataSpider)
c.start()
print(dorms)
file = open('test.csv', 'w', newline ='')
with file:    
    write = csv.writer(file)
    for key in keylist:
        write.writerows([dorms[key]])
