# -*- coding: utf-8 -*-

import os
from os.path import join
import re
import random

import js2py
from scrapy.spiders import CrawlSpider
from scrapy import Request
from scrapy import FormRequest
from scrapy.shell import inspect_response

from googleart_scraper.items import ArtistItem
from googleart_scraper.items import ArtworkItem
from googleart_scraper.items import VisitedUrlItem
from googleart_scraper import settings


class GoogleartCrawlSpider(CrawlSpider):
    name = 'googleart'
    BASE_URL = u'https://www.google.com/culturalinstitute/beta/'
    LOGIN_PAGE = u'https://accounts.google.com/ServiceLogin?service=cultural'
    assert BASE_URL[-1] == '/'
    # allowed_domains = ['google.com']
    NUM_ARTISTS_TO_GET = 6000
    START_URLS = [('https://www.google.com/culturalinstitute/beta/u/0/api/objects/'
                   'category?categoryId=artist&s={}&tab=pop&o=0&hl=en&_reqid=508028&rt=j')
        .format(NUM_ARTISTS_TO_GET)]

    artist_id_reg = re.compile(r'entity/([a-zA-Z].+?)(?:[?/]|$)')
    is_logged_in = False
    is_logging_in_started = False

    def start_requests(self):
        self.logger.debug('===start_requests===')
        if settings.SHOULD_LOGIN_GOOGLE:
            yield self.login()
        else:
            for url in self.START_URLS:
                yield Request(url, callback=self.parse_artists_json, dont_filter=True)

    def login(self):
        self.is_logging_in_started = True
        return Request(url=self.LOGIN_PAGE, callback=self.login_email,
                      dont_filter=True, priority=9999)

    def login_email(self, response):
        self.logger.debug('===login_email===')
        return FormRequest.from_response(response,
                                          formdata={'Email': settings.GOOGLE_ACCOUNT['email']},
                                          callback=self.login_password, dont_filter=True,
                                          priority=9999)

    def login_password(self, response):
        self.logger.debug('===login_password===')
        self.logger.debug('Email: %s', response.xpath('//*[@id="email-display"]').extract())
        self.logger.debug('Error msg: %s',
                          response.xpath('//*[@role="alert" or @class="error-msg"]/text()').extract())
        return [FormRequest.from_response(response,
                                          formdata={'Passwd': settings.GOOGLE_ACCOUNT['password']},
                                          callback=self.after_login,
                                          dont_filter=True, priority=9999)]

    def after_login(self, response):
        email_tag = response.xpath('//*[@id="email-display"]').extract()
        print 'Email:', email_tag
        self.logger.debug('Email: %s', email_tag)
        self.logger.debug('Error msg: %s',
                          response.xpath('//*[@role="alert" or @class="error-msg"]/text()').extract())
        if (email_tag
            or "authentication failed" in response.body
            or 'Wrong password' in response.body
            or 'Das Passwort ist falsch' in response.body):
            self.logger.error("Login failed")
            self.is_logging_in_started = False
            return
        else:
            print("Login Successful!!")
            self.is_logging_in_started = False
            self.is_logged_in = True
            for url in self.START_URLS:
                yield Request(url, callback=self.parse_artists_json, dont_filter=True)

    def parse_artists_json(self, response):

        body = response.body.decode('utf-8').strip()
        if body.startswith(')]}\''):
            body = body[4:]
        js_array = js2py.eval_js(body)
        artists_array = js_array[0][0][2]

        for artist_obj in artists_array:
            url = GoogleartCrawlSpider.BASE_URL + artist_obj[3].strip('/')
            yield Request(url, callback=self.parse_artist)

    @staticmethod
    def get_next_images_page_url(artist_id, next_image_idx, next_page_id, request_id):
        """ Form a request url to get a json with the next page of images data """
        artist_id_pref = artist_id[0]  # first letter of the artist id
        artist_id_suf = artist_id[1:]
        return GoogleartCrawlSpider.BASE_URL + \
               (u'api/entity/assets?entityId=%2F{artist_id_pref}%2F{artist_id_suf}'
                u'&categoryId=artist&s=18&o={next_image_idx}&'
                u'pt={next_page_id}&hl=en&_reqid={request_id}&rt=j'
                .format(artist_id_pref=artist_id_pref, artist_id_suf=artist_id_suf,
                        next_image_idx=next_image_idx,
                        next_page_id=next_page_id, request_id=request_id))

    @staticmethod
    def build_artwork_item(artwork_obj, artist_slug):
        artwork_item = ArtworkItem()
        artwork_item['title'] = artwork_obj[0]
        artwork_item['artist_slug'] = artist_slug
        artwork_item['artist_name_extra'] = artwork_obj[1]
        artwork_item['image_url'] = artwork_obj[2].strip('/')
        if (not artwork_item['image_url'].startswith('http://') and
            not artwork_item['image_url'].startswith('https://')):
            artwork_item['image_url'] = 'https://' + artwork_item['image_url']
        artwork_item['page_url'] = GoogleartCrawlSpider.BASE_URL + artwork_obj[3].strip('/')
        page_url_parts = artwork_obj[3].strip('/').split('/')
        if page_url_parts[-2] == 'asset':
            artwork_item['artwork_slug'] = page_url_parts[-1]
        else:
            artwork_item['artwork_slug'] = '_'.join(page_url_parts[-2:])
        artwork_item['image_id'] = artist_slug + '_' + artwork_item['artwork_slug']
        return artwork_item

    def parse_artist(self, response):
        # if settings.SHOULD_LOGIN_GOOGLE and not self.is_logged_in and not self.is_logging_in_started:
        #     yield self.login()

        artist_id = re.findall(self.artist_id_reg, response.url)[0]
        request_id = '{:04d}'.format(random.randint(0, 9999))
        # TODO:
        name = response.xpath('//*[@id="yDmH0d"]/div[3]/header/div[2]/h1/text()').extract_first()
        print 'Artist name:', name
        years_of_life = response.xpath('//*[@id="yDmH0d"]/div[3]/header/div[2]/h2/text()').extract_first()
        bio = '\n'.join(response.xpath('//*[@id="yDmH0d"]/div[3]/div/div[1]/div/div[1]/text()').extract())
        wiki_url = response.xpath('//*[@id="yDmH0d"]/div[3]/div/div[1]/div/div[2]/a/@href').extract_first()

        script_str = response.xpath('//script[@type="text/javascript"]/text()').extract()[1]
        assert script_str.startswith('window.INIT_data'), \
            'Found the wrong script: {}'.format(script_str[:40])
        js_array = js2py.eval_js(script_str.replace('window.INIT_data', 'INIT_data'))

        artworks_array = js_array[2]
        next_image_idx = js_array[3]
        next_page_id = js_array[5]

        artist_item = ArtistItem()
        artist_item['artist_id'] = artist_id
        artist_item['name'] = name
        artist_slug = name.lower().replace(' ', '-')
        artist_item['years_of_life'] = years_of_life
        artist_item['bio'] = bio
        artist_item['page_url'] = response.url
        artist_item['wiki_url'] = wiki_url
        yield artist_item
        # inspect_response(response, self)

        for artwork_obj in artworks_array:
            artwork_item = self.build_artwork_item(artwork_obj, artist_slug)
            artwork_item['artist_id'] = artist_id
            yield artwork_item
            yield Request(artwork_item['image_url'],
                          callback=self.parse_image,
                          meta={'image_id': artwork_item['image_id']}, priority=10)
            yield Request(artwork_item['page_url'], callback=self.parse_artwork,
                          meta={'image_id': artwork_item['image_id']})

        next_page_url = self.get_next_images_page_url(artist_id=artist_id,
                                                      next_image_idx=next_image_idx,
                                                      next_page_id=next_page_id,
                                                      request_id=request_id)
        yield Request(next_page_url, self.parse_artworks_page_json,
                      meta={'artist_id': artist_id,
                            'artist_slug': artist_slug})

    def parse_artworks_page_json(self, response):
        # if settings.SHOULD_LOGIN_GOOGLE and not self.is_logged_in and not self.is_logging_in_started:
        #     yield self.login()

        """ Parse a json with containing a list of artworks of the current page """
        body = response.body.decode('utf-8').strip()
        if body.startswith(')]}\''):
            body = body[4:]
        js_array = js2py.eval_js(body)
        artworks_array = js_array[0][0][2]
        next_image_idx = js_array[0][0][3]
        next_page_id = js_array[0][0][5]
        request_id = '{:04d}'.format(random.randint(0, 9999))

        for artwork_obj in artworks_array:
            artwork_item = self.build_artwork_item(artwork_obj, response.meta['artist_slug'])
            yield artwork_item
            yield Request(artwork_item['image_url'],
                          callback=self.parse_image,
                          meta={'image_id': artwork_item['image_id']})
            yield Request(artwork_item['page_url'], callback=self.parse_artwork,
                          meta={'image_id': artwork_item['image_id']})

        next_page_url = self.get_next_images_page_url(artist_id=response.meta['artist_id'],
                                                      next_image_idx=next_image_idx,
                                                      next_page_id=next_page_id,
                                                      request_id=request_id)
        yield Request(next_page_url, self.parse_artworks_page_json, meta=response.meta)

    def parse_artwork(self, response):
        # if settings.SHOULD_LOGIN_GOOGLE and not self.is_logged_in and not self.is_logging_in_started:
        #     yield self.login()

        script_str = response.xpath('//script[@type="text/javascript"]/text()').extract()[1]
        assert script_str.startswith('window.INIT_data'), \
            'Found the wrong script: {}'.format(script_str[:40])
        js_array = js2py.eval_js(script_str.replace('window.INIT_data', 'INIT_data'))
        artwork_obj = js_array[2]
        artwork_description = js_array[2][11]

        artwork_item = ArtworkItem()
        artwork_item['image_id'] = response.meta['image_id']
        artwork_item['title'] = artwork_obj[1]
        artwork_item['date'] = artwork_obj[2]
        artwork_item['other'] = dict()

        def get_list_property(prop, append=None):
            l = [x.lower() for x in prop[1][0] if x and not isinstance(x, list)]
            if append:
                l.extend(append)
            return l

        # inspect_response(response, self)

        prop_map = {
            ('theme'): 'theme',
            ('datierung', 'date created', 'datum'): 'date',
            ('original_title'): 'title_original',
            ('entstehungsort', 'location created'): 'location_created',
            ('subject'): ['subject', 'list'],
            ('abmessungen', 'physical dimensions', 'dimensions'): 'dimensions',
            ('typ', 'type'): ['type', 'list'],
            ('material', 'medium', 'support', 'media', 'materials_&_techniques'
             'teknik', 'technik und material'): ['medium', 'list'],
            ('classification', 'object_classification'): 'classification',
            ('artist school', 'school'): 'school',
            ('artist nationality', 'work nationality'): 'nationality',
            ('artist details'): 'artist_details',
            ('stil', 'style'): ['style', 'list'],
            ('object type'): ['object_type', 'list'],
            ('keywords', 'tags'): ['keywords', 'list'],
            ('curatorial_area'): ['curratorial_area', 'list'],
            ('chronology'): 'chronology',
        }

        props_to_skip = ['rechte', 'provenienz', 'herkunft', u'künstler-informationen',
                         'externer link', 'rights', 'artist information', 'provenance',
                         'external link', 'title', 'further_information', 'acquisition_method',
                         'date', 'artist', 'inscriptions', 'null', 'title', 'inventory_number',
                         'artist_biography', 'creator', 'terms_of_use', 'location',
                         'artist/maker', 'title_in_swedish', 'credit_line', 'exhibition',
                         'curator', 'proveniens', 'dansk_link', 'dansk_titel', 'work_notes',
                         'attributed_to', 'title_in_swedish', 'signature', 'periodic_title',
                         'full_title', 'credit_line', 'artwork_accession_number',
                         'object_credit_line', 'bibliography', 'creator', 'external_link'
                         ]
        words_to_skip = ['signature', 'inscription', 'accession', 'credit',
                          'exhibition', 'title', 'rights', 'terms', 'museum', 'inventory']

        for cur_property in artwork_description:
            cur_property[0] = cur_property[0].lower()
            stored = False
            for key, val in prop_map.iteritems():
                if cur_property[0] in key:
                    if isinstance(val, list):
                        field_name, method = val
                        if method == 'list':
                            artwork_item[field_name] = get_list_property(cur_property,
                                                       append=artwork_item.get(field_name, []))
                        else:
                            raise ValueError('Unknown method: {}'.format(method))
                    else:
                        field_name = val
                        artwork_item[field_name] = cur_property[1][0][0]
                    stored = True
                    break
            if not stored:
                should_skip = False
                for skip_word in words_to_skip:
                    if skip_word in cur_property[0]:
                        should_skip = True
                        break
                should_skip |= cur_property[0] not in props_to_skip
                if not should_skip:
                    prop_name = cur_property[0].replace(' ', '_')
                    artwork_item['other'][prop_name] = get_list_property(cur_property)
        yield artwork_item
        yield VisitedUrlItem(url=response.url)

    def parse_image(self, response):
        """ Save image to disk """
        image_path = join(settings.IMAGES_DIR, response.meta['image_id'] + '.jpg')
        if not os.path.exists(image_path):
            with open(image_path, 'wb') as f:
                f.write(response.body)
                self.logger.info('Downloaded image %s', image_path)
            return VisitedUrlItem(url=response.url)
