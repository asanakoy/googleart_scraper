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


class MongoDBPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection_artworks = db[settings['MONGODB_COLLECTION_ARTWORKS']]
        self.collection_artists = db[settings['MONGODB_COLLECTION_ARTISTS']]

    def process_item(self, item, spider):
        for data in item:
            if not data:
                raise DropItem("Missing {0}!".format(data))

        if isinstance(item, ArtistItem):
            self.collection_artists.update({'artist_id': item['artist_id']}, dict(item), upsert=True)
            logging.debug("Artist added to MongoDB database!")
        elif isinstance(item, ArtworkItem):
            self.collection_artworks.update({'image_id': item['image_id']}, dict(item), upsert=True)
            logging.debug("Artwork added to MongoDB database!")
        return item
