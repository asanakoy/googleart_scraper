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
from googleart_scraper.dupefilters import url_hash
from googleart_scraper import settings
from googleart_scraper.items import VisitedUrlItem


if __name__ == '__main__':
    IMAGES_DIR = "/export/home/asanakoy/workspace/googleart/images"

    connection = pymongo.MongoClient(
        settings.MONGODB_SERVER,
        settings.MONGODB_PORT
    )
    db = connection[settings.MONGODB_DB]
    collection_artworks = db[settings.MONGODB_COLLECTION_ARTWORKS]
    collection_artworks.create_index('image_id', unique=True)
    collection_visited_urls = db[settings.MONGODB_VISITED_URLS]

    all_artworks = list(collection_artworks.find())
    print 'All artworks:', len(all_artworks)

    artworks_df = pd.DataFrame(all_artworks)
    artworks_df.index = artworks_df['image_id']

    exist_img_names = glob.glob1('/export/home/asanakoy/workspace/googleart/images', '*.jpg')
    print 'exist_img_paths', len(exist_img_names)
    img_ids = map(lambda x: x[:-4].decode('utf-8'), exist_img_names)
    pprint(img_ids[:10])

    bulk = collection_visited_urls.initialize_ordered_bulk_op()
    for cur_id in tqdm(img_ids):
        if cur_id in artworks_df.index:
            cur_artwork = artworks_df.loc[cur_id].to_dict()
            visited_url_item = VisitedUrlItem()
            visited_url_item['url'] = cur_artwork['image_url']
            visited_url_item['hash'] = url_hash(cur_artwork['image_url'])

            bulk.find({'hash': visited_url_item['hash']}).upsert() \
                        .update_one({'$set': visited_url_item})
    try:
        result = bulk.execute()
    except BulkWriteError as e:
        print e.message
    finally:
        pprint(result)
