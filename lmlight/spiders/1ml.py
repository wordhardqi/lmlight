import scrapy
import pandas as pd
import urllib.parse as urlparse
import csv
import json

def convertToCSV(node_list_txt, to):
    with open(node_list_txt,"r") as f:
        content = f.readlines()
    header = content[0]
    content = content[1:]
    fieldsnames = str.split(header,"\t")
    fieldsnames = list(map(lambda y: y.strip("\n"), fieldsnames))
    fieldsnames = list(filter(lambda x:x!='', fieldsnames))
    print(fieldsnames)

    with open(to,"w") as csv_file:
        writer = csv.DictWriter(csv_file,fieldnames=fieldsnames)
        writer.writeheader()
        for line in content:

            x = str.split(line,"\t")
            x = list(map(lambda y: y.strip("\n"),x))
            row = dict(zip(fieldsnames,x))

            writer.writerow(row)

def getNodeUrlList(node_list_csv):

    nodeNames = pd.read_csv(node_list_csv)["pubkey"].tolist()
    root = "https://1ml.com/node/"
    return list(map(lambda x: urlparse.urljoin(root,x),nodeNames))




class MlSpider(scrapy.Spider):
    name = "1ml_spider"
    def start_requests(self):
        node_list_csv = "/home/renming/lmlight/data/robtex_nodelist_6.25.csv"
        nodeUrLList = getNodeUrlList(node_list_csv)
        # nodeUrLList = nodeUrLList[0:3]
        for url in nodeUrLList:
            yield scrapy.Request(url=url, callback=self.parse)
    def parse(self,response):
        if "node" in response.request.url:
            channels = response.xpath("//a[contains(text(),'Channel Id:')]/@href").extract()
            channleStates = response.xpath("//a[contains(text(),'Channel Id:')]/parent::span/following-sibling::span/text()").extract()

            root = "https://1ml.com/"
            channelUrls =    list(map(lambda x: urlparse.urljoin(root,x),channels))
            for url,state in zip(channelUrls,channleStates):
                yield scrapy.Request(url, meta = {"state":state})
        if "channel" in response.request.url and "json" not in response.request.url:
            cinf = {}
            cinf["LastUpdate"]=response.xpath(
                "//*[contains(text(), 'Last Update')]/following-sibling::*/text()"
            ).extract_first()
            cinf["FirstSeen"] = response.xpath(
                "//*[contains(text(), 'First Seen')]/following-sibling::*/text()"
            ).extract_first()
            cinf["state"] = response.meta["state"]
            # cinf["FirstSeen"] = response.xpath(
            #     "//*[contains(text(), 'First Seen')]/following-sibling::*/text()"
            # ).extract_first()

            yield scrapy.Request(response.request.url+"/json",meta=cinf)
        if "channel" in response.request.url and "json"  in response.request.url:
            channel_info = response.body_as_unicode()
            channel_info = json.loads(channel_info)
            channel_info["channel_id"] = str(channel_info["channel_id"])
            channel_info.update(response.meta)

            yield channel_info



# if __name__ =="__main__":
#     node_list_file = "/home/renming/lmlight/data/robtex_nodelist_6.25.txt"
#     node_list_csv = "/home/renming/lmlight/data/robtex_nodelist_6.25.csv"
#     convertToCSV(node_list_file, node_list_csv)
#     nodeList = getNodeUrlList(node_list_csv)
#     print(nodeList)
