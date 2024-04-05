import csv
import pandas as pd

#file_name = input("DOMAINWHITELIST CSV File Location : ")
# file_name = ("whitelist.csv")
# top_urls = []
# with open(file_name) as file:
#             reader = csv.reader(file)
#             next(reader)  # Skip header row
#             for website in reader:
#                 top_urls.append(website[0])

top_urls = [
    "instagram.com",
    "twitter.com",
    "tiktok.com",
    "linktr.ee",
    "allmylinks.com",
    "fansmetrics.com",
    "onlyfans.com",
    "pornhub.com",
    "hubite.com",
    "hotwifelexilove.com",
    "manyvids.com",
    "clips4sale.com",
    "m.facebook.com",
    "facebook.com",
    "mindiminkxxx.com",
    "tour.mindiminkxxx.com",
    "shopmindimink.com",
    "cameo.com",
    "iwantclips.com",
    "patreon.com",
    "bestfans.com",
    "myfreecams.com",
    "jerkmate.com",
    "chaturbate.com",
    "passes.com",
    "youtube.com"
]

#file = input('WORK URLS Excel File Location : ')

def get_successlist(urls):
    success_list = []
    for i in range(len(urls)):#read working urls 
        url = urls[i].strip()
        exists = False
        for top_url in top_urls:#check whitedomian exists or not in url
            if(top_url in url):
                exists = True
                break
        if(not exists):#exclude whitedomain urls
            success_list.append(url)

    return success_list


