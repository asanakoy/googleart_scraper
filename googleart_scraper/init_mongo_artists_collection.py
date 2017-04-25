import re
import glob
from pprint import pformat
import os
from os.path import join
import pandas as pd
from pprint import pprint
import requests

import js2py
import pymongo
from pymongo.errors import BulkWriteError
from tqdm import tqdm

from googleart_scraper.spiders.crawler import GoogleartCrawlSpider
from googleart_scraper import settings


def parse_artists_json(body):
    body = body.decode('utf-8').strip()
    if body.startswith(')]}\''):
        body = body[4:]
    print 'Parsing json (can take several minutes)'
    js_array = js2py.eval_js(body)
    artists_array = js_array[0][0][2]
    print 'json parsed!'

    artists = list()
    for artist_obj in artists_array:
        artist_item = dict()
        artist_item['name'] = artist_obj[0].strip()
        artist_item['page_url'] = GoogleartCrawlSpider.BASE_URL + artist_obj[3].strip('/')
        artist_item['artist_id'] = GoogleartCrawlSpider.artist_id_from_page_url(artist_item['page_url'])
        artist_item['total_items_count'] = int(artist_obj[1].strip().split(' ')[0].replace(',', ''))
        artists.append(artist_item)
    return artists


if __name__ == '__main__':
    IMAGES_DIR = "/export/home/asanakoy/workspace/googleart/images"

    connection = pymongo.MongoClient(
        settings.MONGODB_SERVER,
        settings.MONGODB_PORT
    )
    db = connection[settings.MONGODB_DB]
    collection_artworks = db[settings.MONGODB_COLLECTION_ARTWORKS]
    collection_artworks.create_index('image_id', unique=True)
    collection_artists = db[settings.MONGODB_COLLECTION_ARTISTS]
    collection_artists.create_index('artist_id', unique=True)

    all_artworks = list(collection_artworks.find())
    print 'All artworks:', len(all_artworks)

    artists_df_path = '/export/home/asanakoy/workspace/googleart/info/artists_short.hdf5'
    artist_json_path = '/export/home/asanakoy/workspace/googleart/info/artists_json_response.json'

    if not os.path.exists(artists_df_path):
        if os.path.exists(artist_json_path):
            with open(artist_json_path, mode='r') as f:
                response_body = f.read()
        else:
            raise NotImplementedError()
            # this doesn't work w/o login
            request_url = GoogleartCrawlSpider.START_URLS[0]
            print 'Downloading json:', request_url
            response = requests.get(request_url,
                                    headers=settings.DEFAULT_REQUEST_HEADERS)
            response.encoding = 'utf-8'
            response_body = response.text

        artists_list_from_server = parse_artists_json(response_body)
        artist_df = pd.DataFrame(artists_list_from_server)

        artist_df.index = artist_df['artist_id']
        del artist_df['artist_id']
        # artist_df.to_hdf(artists_df_path, 'df', mode='w')
    else:
        artist_df = pd.read_hdf(artists_df_path)
    artist_df['artist_id'] = artist_df.index

    bulk = collection_artists.initialize_ordered_bulk_op()
    for artist_item in tqdm(artist_df.T.to_dict().values()):
        bulk.find({'artist_id': artist_item['artist_id']}).upsert()\
            .update_one({'$set': artist_item})
    try:
        result = bulk.execute()
    except BulkWriteError as e:
        print e.message
    finally:
        pprint(result)


