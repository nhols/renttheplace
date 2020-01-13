import requests
from bs4 import BeautifulSoup
import numpy as  np

listing_ids = []
search_zones = {'ZONE1':'920364979', 'ZONE2':'920365348', 'ZONE3':'920365945', 'ZONE4':'920366158', 'ZONE5':'920366257', 'ZONE6':'920366374'}

for z in search_zones:

    print(f'Grabbing listing ids for {z}')
    SEARCHID = search_zones[z]

    rsp = requests.get(f'https://www.spareroom.co.uk/flatshare/?search_id={SEARCHID}')
    parsed_rsp = BeautifulSoup(rsp.content, 'html.parser')

    for listing in parsed_rsp.find_all("li", class_="listing-result"):
        listing_ids.append(listing['data-listing-id'])

    RESULTS = int(parsed_rsp.find('p', {'id' : 'results_header'}).contents[3].text)
    PAGE_UPPER = int(np.ceil(RESULTS / 10) * 10 + 1)

    for PAGE in range(1,PAGE_UPPER):

        rsp = requests.get(f'https://www.spareroom.co.uk/flatshare/?offset={PAGE * 10}&search_id={SEARCHID}&sort_by=age')
        parsed_rsp = BeautifulSoup(rsp.content, 'html.parser')

        for listing in parsed_rsp.find_all("li", class_="listing-result"):
            listing_ids.append(listing['data-listing-id'])

