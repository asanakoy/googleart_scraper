import os
import logging

import pymongo

from scrapy.utils.job import job_dir
from scrapy.utils.request import request_fingerprint
from scrapy.dupefilters import RFPDupeFilter

import hashlib
from scrapy.utils.python import to_bytes, to_native_str

from w3lib.url import canonicalize_url


def url_hash(url):
    """
    Return the url hash.

    The request fingerprint is a hash that uniquely identifies the resource the
    request points to. For example, take the following two urls:

    http://www.example.com/query?id=111&cat=222
    http://www.example.com/query?cat=222&id=111

    Even though those are two different URLs both point to the same resource
    and are equivalent (ie. they should return the same response).

    """
    request_method = 'GET'
    fp = hashlib.sha1()
    fp.update(to_bytes(request_method))
    fp.update(to_bytes(canonicalize_url(url)))
    return fp.hexdigest()


class DupeFilter(RFPDupeFilter):
    def __init__(self, settings, debug=False):
        self.file = None
        self.fingerprints = set()
        self.logdupes = True
        self.debug = debug
        self.logger = logging.getLogger(__name__)

        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        visited_urls = db[settings['MONGODB_VISITED_URLS']]
        self.fingerprints = set([x['hash'] for x in visited_urls.find(projection=['hash'])])
        logging.info('DupeFilter: %d visited urls', len(self.fingerprints))
        connection.close()

    @classmethod
    def from_settings(cls, settings):
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls(settings, debug)

    def request_fingerprint(self, request):
        return url_hash(request.url)
