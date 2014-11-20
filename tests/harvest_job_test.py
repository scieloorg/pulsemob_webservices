import unittest
import json
import os
from xylose.scielodocument import Article, Citation, Journal, html_decode
from xylose import tools
from httmock import urlmatch, HTTMock
import requests
from pulsemob_webservices.harvest_job import *

class HarvestJobTests(unittest.TestCase):
    def test_harvest(self):
        @urlmatch(netloc=r'(.*\.)?articlemeta\.scielo\.org$', path=r'^/api/v1/article/identifiers$')
        def article_identifiers_mock(url, request):
            path = os.path.dirname(os.path.realpath(__file__))
            result = open('%s/fixtures/article_identifiers.json' % path).read()
            return result

        with HTTMock(article_identifiers_mock):
            config = ConfigParser.ConfigParser()
            config.read('../harvest.cfg')
            harvest(config.get("harvest", "article_meta_uri"),
            "article",
            config.get("harvest", "data_source_name"),
            "article_data_test",
            config.get("harvest", "pg_shared_folder_output"),
            config.get("harvest", "pg_shared_folder_input"),
            config.get("harvest", "solr_uri")
            )
            # extract_data_from_article_webservice_to_file("http://mockservice/api/v1", "test.txt")
            # r = requests.get('http://mockservice/api/v1/article/identifiers?offset=0')
            # print r.content
