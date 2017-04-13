import os
import logging
import threading

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
    """
    Class for filtering duplicate links.
    Uses database to retrieve visited links of previous / parallel runs.
    """
    def __init__(self, settings, debug=False, sync_every=3600):
        """
        Args:
            settings: scrapper settings
            debug: is debug?
            sync_every: how often to sync visited links with database. In seconds.
        """
        self.file = None
        self.fingerprints = set()
        self.logdupes = True
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        self.sync_every = sync_every

        connection = pymongo.MongoClient(
            self.settings['MONGODB_SERVER'],
            self.settings['MONGODB_PORT']
        )
        self.db = connection[self.settings['MONGODB_DB']]
        self.fingerprints = set()
        self.sync_with_database()

    def sync_with_database(self):
        visited_urls = self.db[self.settings['MONGODB_VISITED_URLS']]
        visited_url_hashes = set([x['hash'] for x in visited_urls.find(projection=['hash'])])
        self.fingerprints = self.fingerprints.union(visited_url_hashes)
        logging.info('Visited links synced with database: %d visited urls', len(self.fingerprints))
        if self.sync_every:
            threading.Timer(self.sync_every, self.sync_with_database).start()

    @classmethod
    def from_settings(cls, settings):
        debug = settings.getbool('DUPEFILTER_DEBUG')
        return cls(settings, debug)

    def request_fingerprint(self, request):
        return url_hash(request.url)
