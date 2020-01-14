import requests
from bs4 import BeautifulSoup
import numpy as np
import re
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


for id in listing_ids:

    rsp = requests.get(f'https://www.spareroom.co.uk/flatshare/flatshare_detail.pl?flatshare_id={id}')
    parsed_rsp = BeautifulSoup(rsp.content, 'html.parser')

    lat = re.findall(r'\"\d+\.\d+\"', parsed_rsp.find_all('script')[2].text)
    lon = re.findall(r'\"-\d+\.\d+\"', parsed_rsp.find_all('script')[2].text)

    for room in parsed_rsp.find_all('li', {'class' : 'room-list__room'}):
        print(room.find('strong').text)
        print(room.find('small').text)

    feature_keys = parsed_rsp.find_all('dt', {'class': 'feature-list__key'})
    feature_values = parsed_rsp.find_all('dt', {'class': 'feature-list__value'})