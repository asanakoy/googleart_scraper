import re
import js2py
import random

artist_id_reg = re.compile(r'entity/([a-zA-Z].+?)(?:[?/]|$)')
def artist_id_from_page_url(url):
        return re.findall(artist_id_reg, url)[0]


BASE_URL = u'https://www.google.com/culturalinstitute/beta/'    
def get_next_images_page_url(artist_id, next_image_idx, next_page_id, request_id):
    """ Form a request url to get a json with the next page of images data """
    artist_id_pref = artist_id[0]  # first letter of the artist id
    artist_id_suf = artist_id[1:]
    return BASE_URL + \
           (u'api/entity/assets?entityId=%2F{artist_id_pref}%2F{artist_id_suf}'
            u'&categoryId=artist&s=1000&o={next_image_idx}&'
            u'pt={next_page_id}&hl=en&_reqid={request_id}&rt=j'
            .format(artist_id_pref=artist_id_pref, artist_id_suf=artist_id_suf,
                    next_image_idx=next_image_idx,
                    next_page_id=next_page_id, request_id=request_id))



artist_id = artist_id_from_page_url(response.url)
request_id = '{:04d}'.format(random.randint(0, 9999))



### PARSE ARTIST PAGE ###
artist_id = artist_id_from_page_url(response.url)
request_id = '{:04d}'.format(random.randint(0, 9999))
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



#####def parse_artworks_page_json(self, response): #####
""" Parse a json with containing a list of artworks of the current page """
body = response.body.decode('utf-8').strip()
if body.startswith(')]}\''):
    body = body[4:]
js_array = js2py.eval_js(body)
artworks_array = js_array[0][0][2]
next_image_idx = js_array[0][0][3]
next_page_id = js_array[0][0][5]
request_id = '{:04d}'.format(random.randint(0, 9999))
