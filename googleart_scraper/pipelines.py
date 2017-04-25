# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging

import pymongo
from scrapy.conf import settings
from scrapy.exceptions import DropItem

from googleart_scraper.items import ArtistItem
from googleart_scraper.items import ArtworkItem
from googleart_scraper.items import VisitedUrlItem
from googleart_scraper.dupefilters import url_hash


class MongoDBPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection_artworks = db[settings['MONGODB_COLLECTION_ARTWORKS']]
        self.collection_artworks.create_index('image_id', unique=True)
        self.collection_artists = db[settings['MONGODB_COLLECTION_ARTISTS']]
        self.collection_artists.create_index('artist_id', unique=True)
        self.collection_visited_urls = db[settings['MONGODB_VISITED_URLS']]
        self.collection_visited_urls.create_index('hash', unique=True)

    def process_item(self, item, spider):
        for data in item:
            if not data:
                raise DropItem("Missing {0}!".format(data))

        if isinstance(item, ArtistItem):
            self.collection_artists.update({'artist_id': item['artist_id']},
                                           {'$set': item},
                                           upsert=True)
            logging.debug("Artist added to MongoDB database!")
        elif isinstance(item, ArtworkItem):
            self.collection_artworks.update_one({'image_id': item['image_id']},
                                                {'$set': item},
                                                upsert=True)
            logging.debug("Artwork added to MongoDB database!")
        elif isinstance(item, VisitedUrlItem):
            item['hash'] = url_hash(item['url'])
            self.collection_visited_urls.insert_one(dict(item))
            # self.collection_visited_urls.update({'hash': item['hash']}, dict(item), upsert=True)
        return item
