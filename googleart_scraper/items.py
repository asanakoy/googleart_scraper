# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field


class ArtworkItem(Item):
    title = Field()
    title_original = Field()
    artist_id = Field()
    artist_slug = Field()
    artist_name_extra = Field()  # can be with some extra info, like pupil, workshop, can be null
    page_url = Field()
    image_url = Field()
    artwork_slug = Field()
    image_id = Field()
    date = Field()  # may be "undated"
    date_extra = Field()
    location_created = Field()
    subject = Field()
    dimensions = Field()
    type = Field()
    medium = Field()
    classification = Field()
    school = Field()
    nationality = Field()
    artist_details = Field()
    style = Field()
    object_type = Field()  # drawing
    other = Field()
    theme = Field()
    keywords = Field()
    curratorial_area = Field()  # [u'prints and drawings']
    chronology = Field()  # '1801-1850'


class ArtistItem(Item):
    name = Field()
    artist_id = Field()
    page_url = Field()
    bio = Field()
    wiki_url = Field()
    years_of_life = Field()


class VisitedUrlItem(Item):
    url = Field()
    hash = Field()
