import pandas as pd
from pandas.io.json import json_normalize
import json
import re

def json_to_df(FP):
    with open(FP) as f:
        data = json.load(f)

    listings = []
    for k in data.keys():
        for r in data[k].keys():
            df_tmp = json_normalize(data[k][r])
            df_tmp['tube_zone'] = k
            listings.append(df_tmp)
        print(f'{k}: {len(data[k])}')

    df = pd.concat(listings, sort=False)

    return df

def clean_listing_df(df):
    new_cols = []
    for f in df.columns.values:
        r = re.sub('\n+|\s+', '', f).strip()
        r = re.sub(r'^features\.', '', r).strip()
        r = r.lower()
        new_cols.append(r)

    df.columns = new_cols

    df.rename(
        columns=
        {
            'key_features.0': 'type',
            'key_features.1': 'location',
            'key_features.2': 'postcode_district',
            'geo.lat': 'latitude',
            'geo.lon': 'longitude'
        }, inplace=True
    )

    df[['tube_station', 'tube_station_walk']] = df['key_features.3'].str.split('\n+', expand=True)

    df['latitude'] = df['latitude'].str.get(0).str.replace('"', '', ).astype(float)
    df['longitude'] = df['longitude'].str.get(0).str.replace('"', '', ).astype(float)
    df['postcode_district'] = df['postcode_district'].str.replace('\(Area info\)', '').str.strip()

    df.drop(['key_features.3', 'key_features.4'], axis=1, inplace=True)

    return df

def get_room_listings(df):

    df_prices = df[['id'] + [c for c in df.columns if 'rooms' in c and 'price' in c]].melt(id_vars='id',
                                                                                           var_name='room_number',
                                                                                           value_name='room_price').dropna()
    df_prices['room_number'] = df_prices['room_number'].str.replace('[^0-9]+', '')

    df_types = df[['id'] + [c for c in df.columns if 'rooms' in c and 'type' in c]].melt(id_vars='id',
                                                                                         var_name='room_number',
                                                                                         value_name='room_type').dropna()
    df_types['room_number'] = df_types['room_number'].str.replace('[^0-9]+', '')

    df_deposits = df[['id'] + [c for c in df.columns if 'deposit(' in c]].melt(id_vars='id',
                                                                               var_name='room_number',
                                                                               value_name='room_deposit').dropna()
    df_deposits['room_number'] = df_deposits['room_number'].str.replace('[^0-9]+', '')

    df_rooms = df_prices.merge(df_types,
                               how='inner',
                               on=['id', 'room_number']).merge(df_deposits,
                                                               how='left',
                                                               on=['id', 'room_number'])

    df_rooms['room_price_pw'] = df_rooms.room_price.str.replace('[^0-9]+', '').astype(int)
    df_rooms['room_price_pcm'] = df_rooms.room_price_pw

    df_rooms.loc[df_rooms.room_price.str.contains('pcm'), 'room_price_pw'] = (
                df_rooms.loc[df_rooms.room_price.str.contains('pcm'), 'room_price_pw'] * 12 / 52).astype(int)
    df_rooms.loc[df_rooms.room_price.str.contains('pw'), 'room_price_pcm'] = (
                df_rooms.loc[df_rooms.room_price.str.contains('pw'), 'room_price_pcm'] * 52 / 12).astype(int)

    return df_rooms

