import requests
from bs4 import BeautifulSoup
import numpy as np
import re
from datetime import datetime
import json

FILE_OUT = 'listing_data_feb.json'


def grab_all_listing_ids(search_id, max_pages=-1):
    listing_ids = []

    rsp = requests.get(f'https://www.spareroom.co.uk/flatshare/?search_id={search_id}')
    parsed_rsp = BeautifulSoup(rsp.content, 'html.parser')

    for listing in parsed_rsp.find_all("li", class_="listing-result"):
        listing_ids.append(listing['data-listing-id'])

    if max_pages > 0:
        PAGE_UPPER = min(100, max_pages)
    else:
        RESULTS = int(re.search('[0-9]+', parsed_rsp.find('p', {'id': 'results_header'}).contents[3].text).group(0))
        PAGE_UPPER = min(100, int(np.ceil(RESULTS / 10) * 10 + 1))

    print(f'looping through {PAGE_UPPER} pages')
    for PAGE in range(1, PAGE_UPPER):
        if PAGE % 10 == 0:
            print(f'Starting id scrape of page {PAGE}')
        rsp = requests.get(
            f'https://www.spareroom.co.uk/flatshare/?offset={PAGE * 10}&search_id={search_id}&sort_by=age')
        parsed_rsp = BeautifulSoup(rsp.content, 'html.parser')

        for listing in parsed_rsp.find_all("li", class_="listing-result"):
            listing_ids.append(listing['data-listing-id'])

    return listing_ids


class ListingScrape:

    def __init__(self, listing_id):
        self.id = listing_id
        self.data = {}

        self.url = f'https://www.spareroom.co.uk/flatshare/flatshare_detail.pl?flatshare_id={self.id}'
        self.rsp = requests.get(self.url)
        self.parsed_rsp = BeautifulSoup(self.rsp.content, 'html.parser')

        self.data['id'] = self.id
        self.data['url'] = self.url

    def grab_key_features(self):

        try:
            # grab key_features of listing
            self.data['key_features'] = {}
            for i, k in enumerate(self.parsed_rsp.find_all('li', {'class': 'key-features__feature'})):
                self.data['key_features'][i] = k.text.strip()
        except:
            print(f"couldn't grab key features for listing with id {id}")

    def grab_geo_data(self):

        try:
            # grab coords of listing
            self.data['geo'] = {}
            lat = re.findall(r'\"\d+\.\d+\"', self.parsed_rsp.find_all('script')[2].text)
            lon = re.findall(r'\"-\d+\.\d+\"', self.parsed_rsp.find_all('script')[2].text)
            self.data['geo']['lat'] = lat
            self.data['geo']['lon'] = lon
        except:
            print(f"couldn't grab lat/lon for listing with id {id}")

    def grab_room_data(self):

        try:
            # grab price, availability and type of spare room
            self.data['rooms'] = {}
            for i, room in enumerate(self.parsed_rsp.find_all('li', {'class': 'room-list__room'})):
                self.data['rooms'][i] = {}
                self.data['rooms'][i]['price'] = room.find('strong').text.strip()
                self.data['rooms'][i]['type'] = room.find('small').text
        except:
            print(f"couldn't grab room prices for listing with id {id}")

    def grab_features(self):

        try:
            # grab extra features about listing
            self.data['features'] = {}
            feature_keys = self.parsed_rsp.find_all('dt', {'class': 'feature-list__key'})
            feature_values = self.parsed_rsp.find_all('dd', {'class': 'feature-list__value'})
            for f, v in zip(feature_keys, feature_values):
                self.data['features'][f.text.strip()] = v.text.strip()
        except:
            print(f"couldn't grab features for listing with id {id}")

    def grab_desc(self):
        try:
            # grab extra features about listing
            self.data['desc'] = self.parsed_rsp.find('p', {'class': 'detaildesc'}).text
        except:
            print(f"couldn't free text desc for listing with id {id}")


def __main__():
    data = {}

    # looks like these change overtime :(
    # update by visiting https://www.spareroom.co.uk/flatshare/
    # Search Zone 1 ... Zone 6 in "Where?" search bar
    # Grab numeric search_id in URL of each tube zone
    search_zones = {'ZONE1': '936018085', 'ZONE2': '936018190', 'ZONE3': '936018286', 'ZONE4': '936018370',
                    'ZONE5': '936018490', 'ZONE6': '936018580'}

    for z in search_zones.keys():
        print(f'grabbing ids for tube zone {z}\n{datetime.now()}')
        ids = grab_all_listing_ids(search_zones[z])
        print(f'{len(ids)} ids for tube zone {z} successfully scraped\n{datetime.now()}')

        data[z] = {}
        for id in ids:
            scrape = ListingScrape(id)
            scrape.grab_key_features()
            scrape.grab_room_data()
            scrape.grab_geo_data()
            scrape.grab_features()
            scrape.grab_desc()
            data[z][id] = scrape.data

    return data


if __name__ == '__main__':
    data = __main__()
    with open(FILE_OUT, 'w') as fp:
        json.dump(data, fp)
