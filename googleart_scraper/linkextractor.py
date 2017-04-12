import re
import logging
from six.moves.urllib.parse import urlparse, urljoin
import lxml.etree as etree

from scrapy.link import Link
import scrapy.linkextractors
import scrapy.linkextractors.lxmlhtml
from scrapy.utils.response import get_base_url
from scrapy.utils.python import unique as unique_list, to_native_str
from scrapy.utils.misc import arg_to_iter
from scrapy.shell import inspect_response

_collect_string_content = etree.XPath("string()")
_re_type = type(re.compile("", 0))


class ParserLinkExtractor(scrapy.linkextractors.lxmlhtml.LxmlParserLinkExtractor):
    """
    Class to extracting links from tag <script type="text/javascript">...</script>.
    This links are stored in javascript array, not in html tags.
    The class extracts links from the body of the tag using list of regular expressions `url_regexps`.
    """

    def __init__(self, url_regexps, process=None, unique=False):
        self.url_regexps = url_regexps
        self.process_attr = process if callable(process) else lambda v: v
        self.unique = unique

    def _iter_links(self, document):
        scripts = document.xpath('//script[@type="text/javascript"]/text()').extract()
        if not scripts:
            logging.warning('Scripts not found!')
        array_text = None
        for script in scripts:
            if script.startswith('window.INIT_data'):
                # TODO: evaluate javascript properly
                array_text = script.replace(u'\\u003d', u'=')
                break
        if array_text is None:
            print scripts
            logging.warning('Links not found!')
            return []
        else:
            all_urls = []
            for regexp in self.url_regexps:
                all_urls.extend(re.findall(regexp, array_text))
            print 'URLs:', all_urls[:10]
            return all_urls

    def _extract_links(self, selector, response_url, response_encoding, base_url):
        links = []
        # hacky way to get the underlying lxml parsed document
        for attr_val in self._iter_links(selector):
            # pseudo lxml.html.HtmlElement.make_links_absolute(base_url)
            try:
                attr_val = urljoin(base_url, attr_val)
            except ValueError:
                continue  # skipping bogus links
            else:
                url = self.process_attr(attr_val)
                if url is None:
                    continue
            url = to_native_str(url, encoding=response_encoding)
            # to fix relative links after process_value
            url = urljoin(response_url, url)
            link = Link(url, u'', nofollow=False)
            links.append(link)
        return self._deduplicate_if_needed(links)


class GoogleApiLinkExtractor(scrapy.linkextractors.FilteringLinkExtractor):
    def __init__(self, allow=(), deny=(), allow_domains=(), deny_domains=(), restrict_xpaths=(),
                 canonicalize=True, unique=True, process_value=None, deny_extensions=None, restrict_css=(),
                 base_url=None):
        """ `allow` specifies which regexps to use to extract links """
        allow_res = [x if isinstance(x, _re_type) else re.compile(x) for x in arg_to_iter(allow)]

        lx = ParserLinkExtractor(allow_res, unique=unique, process=process_value)

        super(GoogleApiLinkExtractor, self).__init__(lx, allow=allow_res, deny=deny,
            allow_domains=allow_domains, deny_domains=deny_domains,
            restrict_xpaths=restrict_xpaths, restrict_css=restrict_css,
            canonicalize=canonicalize, deny_extensions=deny_extensions)
        self.base_url = base_url

    def extract_links(self, response):
        # TODO: remove debug code
        with open('/export/home/asanakoy/tmp/response.txt', 'w') as f:
            f.write(response.body)
        assert False, 'enough ;)'
        base_url = self.base_url if self.base_url else get_base_url(response)
        if self.restrict_xpaths:
            docs = [subdoc
                    for x in self.restrict_xpaths
                    for subdoc in response.xpath(x)]
        else:
            docs = [response.selector]
        all_links = []
        for doc in docs:
            links = self._extract_links(doc, response.url, response.encoding, base_url)
            print 'Num links before filter:', len(links)
            all_links.extend(self._process_links(links))
        print 'Num links:', len(all_links)
        return unique_list(all_links)
