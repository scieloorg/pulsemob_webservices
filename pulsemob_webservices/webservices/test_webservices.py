__author__ = 'vitor'

from pprint import pprint
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
import json
import ConfigParser
from models import *

config = ConfigParser.ConfigParser()
config.read('webservices/test_webservices.cfg')

facebook_id = config.get("test_webservices", "facebook_id")
facebook_token = config.get("test_webservices", "facebook_token")
google_id = config.get("test_webservices", "google_id")
google_token = config.get("test_webservices", "google_token")
email = config.get("test_webservices", "email")
name = config.get("test_webservices", "name")
font_size = config.get("test_webservices", "font_size")
language = config.get("test_webservices", "language")


def insert_feed_publications():
            # Inserting feeds.
        feed_1 = Feed(None, "Human Sciences", "Ciencias Humanas", "Humanidades")
        feed_2 = Feed(None, "Biological Sciences", "Ciencias Biologicas", "Ciencias Biologicas")
        feed_3 = Feed(None, "Health Sciences", "Ciencias da Saude", "Ciencias de la Salud")

        feed_1.save()
        feed_2.save()
        feed_3.save()

        # Inserting publications
        publication_1 = Publication(1, 'Old Testament Essays')
        publication_2 = Publication(2, 'Samj: South African Medical Journal')
        publication_3 = Publication(3, 'South African Journal Of Psychiatry')
        publication_5 = Publication(5, 'Acta Theologica')
        publication_6 = Publication(6, 'South African Journal Of Occupational Therapy')
        publication_7 = Publication(7, 'Water Sa')
        publication_8 = Publication(8, 'Escola Anna Nery')
        publication_9 = Publication(9, 'Brazilian Journal Of Otorhinolaryngology')
        publication_18 = Publication(18, 'Crop Breeding And Applied Biotechnology')
        publication_22 = Publication(22, 'Trabalho, Educacao E Saude')
        publication_23 = Publication(23, 'Brazilian Journal Of Medical And Biological Research')
        publication_24 = Publication(24, 'Anales Del Instituto De Investigaciones Esteticas')

        publication_1.save()
        publication_2.save()
        publication_3.save()
        publication_5.save()
        publication_6.save()
        publication_7.save()
        publication_8.save()
        publication_9.save()
        publication_18.save()
        publication_22.save()
        publication_23.save()
        publication_24.save()

        # Insert relations
        publication_1.feeds.add(feed_1)
        publication_2.feeds.add(feed_2)
        publication_2.feeds.add(feed_3)
        publication_3.feeds.add(feed_3)
        publication_5.feeds.add(feed_1)
        publication_6.feeds.add(feed_2)
        publication_6.feeds.add(feed_3)
        publication_7.feeds.add(feed_1)
        publication_7.feeds.add(feed_2)
        publication_8.feeds.add(feed_3)
        publication_9.feeds.add(feed_3)
        publication_18.feeds.add(feed_2)
        publication_22.feeds.add(feed_1)
        publication_23.feeds.add(feed_2)
        publication_24.feeds.add(feed_1)


class Tests(APITestCase):
    def test_case1(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Login didn't work.")

        response_dict = json.loads(response._container[0])

        self.assertEqual(response_dict['user']['facebook_id'], facebook_id, "Facebook id doesn't match.")
        self.assertEqual(response_dict['user']['email'], email, "Email doesn't match.")
        self.assertEqual(response_dict['user']['name'], name, "Name doesn't match.")
        self.assertEqual(response_dict['user']['font_size'], font_size, "Font size doesn't match.")
        self.assertEqual(response_dict['user']['language'], language, "Language doesn't match.")

    def test_case2(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "First login didn't work.")

        response_dict1 = json.loads(response._container[0])

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Second login didn't work.")

        response_dict2 = json.loads(response._container[0])

        self.assertEqual(response_dict2['user']['id'], response_dict1['user']['id'], "ID doesn't match.")
        self.assertEqual(response_dict2['user']['facebook_id'], response_dict1['user']['facebook_id'], "Facebook id doesn't match.")
        self.assertEqual(response_dict2['user']['email'], response_dict1['user']['email'], "Email doesn't match.")
        self.assertEqual(response_dict2['user']['name'], response_dict1['user']['name'], "Name doesn't match.")
        self.assertEqual(response_dict2['user']['font_size'], response_dict1['user']['font_size'], "Font size doesn't match.")
        self.assertEqual(response_dict2['user']['language'], response_dict1['user']['language'], "Language doesn't match.")

    def test_case3(self):
        client = APIClient()
        client.credentials(HTTP_GOOGLEID=google_id, HTTP_TOKEN=google_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Login didn't work.")

        response_dict = json.loads(response._container[0])

        self.assertEqual(response_dict['user']['google_id'], google_id, "Google id doesn't match.")
        self.assertEqual(response_dict['user']['email'], email, "Email doesn't match.")
        self.assertEqual(response_dict['user']['name'], name, "Name doesn't match.")
        self.assertEqual(response_dict['user']['font_size'], font_size, "Font size doesn't match.")
        self.assertEqual(response_dict['user']['language'], language, "Language doesn't match.")

    def test_case4(self):
        client = APIClient()
        client.credentials(HTTP_GOOGLEID=google_id, HTTP_TOKEN=google_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "First login didn't work.")

        response_dict1 = json.loads(response._container[0])

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Second login didn't work.")

        response_dict2 = json.loads(response._container[0])

        self.assertEqual(response_dict2['user']['id'], response_dict1['user']['id'], "ID doesn't match.")
        self.assertEqual(response_dict2['user']['google_id'], response_dict1['user']['google_id'], "Google id doesn't match.")
        self.assertEqual(response_dict2['user']['email'], response_dict1['user']['email'], "Email doesn't match.")
        self.assertEqual(response_dict2['user']['name'], response_dict1['user']['name'], "Name doesn't match.")
        self.assertEqual(response_dict2['user']['font_size'], response_dict1['user']['font_size'], "Font size doesn't match.")
        self.assertEqual(response_dict2['user']['language'], response_dict1['user']['language'], "Language doesn't match.")

    def test_case5(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "First login didn't work.")

        response_dict1 = json.loads(response._container[0])

        client = APIClient()
        client.credentials(HTTP_GOOGLEID=google_id, HTTP_TOKEN=google_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Second login didn't work.")

        response_dict2 = json.loads(response._container[0])

        self.assertEqual(response_dict2['user']['id'], response_dict1['user']['id'], "ID doesn't match.")
        self.assertEqual(response_dict2['user']['facebook_id'], response_dict1['user']['facebook_id'], "Facebook id doesn't match.")
        self.assertEqual(response_dict2['user']['email'], response_dict1['user']['email'], "Email doesn't match.")
        self.assertEqual(response_dict2['user']['name'], response_dict1['user']['name'], "Name doesn't match.")
        self.assertEqual(response_dict2['user']['font_size'], response_dict1['user']['font_size'], "Font size doesn't match.")
        self.assertEqual(response_dict2['user']['language'], response_dict1['user']['language'], "Language doesn't match.")

    def test_case6(self):
        client = APIClient()
        client.credentials(HTTP_GOOGLEID=google_id, HTTP_TOKEN=google_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "First login didn't work.")

        response_dict1 = json.loads(response._container[0])

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Second login didn't work.")

        response_dict2 = json.loads(response._container[0])

        self.assertEqual(response_dict2['user']['id'], response_dict1['user']['id'], "ID doesn't match.")
        self.assertEqual(response_dict2['user']['facebook_id'], facebook_id, "Facebook id doesn't match.")
        self.assertEqual(response_dict2['user']['google_id'], google_id, "Google id doesn't match.")
        self.assertEqual(response_dict2['user']['email'], response_dict1['user']['email'], "Email doesn't match.")
        self.assertEqual(response_dict2['user']['name'], response_dict1['user']['name'], "Name doesn't match.")
        self.assertEqual(response_dict2['user']['font_size'], response_dict1['user']['font_size'], "Font size doesn't match.")
        self.assertEqual(response_dict2['user']['language'], response_dict1['user']['language'], "Language doesn't match.")

    def test_case7(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN='invalidtoken')

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_200_OK, "Login shouldn't work.")

    def test_case8(self):
        client = APIClient()
        client.credentials(HTTP_GOOGLEID=google_id, HTTP_TOKEN='invalidtoken')

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_200_OK, "Login shouldn't work.")

    def test_case9(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        insert_feed_publications()

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.get('/home/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, "/home/ didn't work.")

    def test_case10(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.get('/solr/version', {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/solr/version didn't work.")

    def test_case11(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/favorite/create', {'article_id': 'S0102-76382014000300344scl'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/favorite/create didn't work.")

    def test_case12(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.get('/favorite/read', {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/favorite/read didn't work.")

    def test_case13(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/favorite/create', {'article_id': 'S0102-76382014000300344scl'}, format='json')
        response = client.get('/favorite/read', {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/favorite/read didn't work.")

    def test_case14(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/favorite/create', {'article_id': 'S0102-76382014000300344scl'}, format='json')
        response = client.post('/favorite/delete', {'article_id': 'S0102-76382014000300344scl'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/favorite/delete didn't work.")

    def test_case15(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        insert_feed_publications()

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.get('/feed/publications/list', {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/feed/publications/list didn't work.")

        #
    def test_case16(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        insert_feed_publications()

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/preferences/feed/exclusion/create', {'feed_id': 1}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/preferences/feed/exclusion/create didn't work.")

    def test_case17(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        insert_feed_publications()

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/preferences/feed/exclusion/create', {'feed_id': 1}, format='json')
        response = client.post('/preferences/feed/exclusion/delete', {'feed_id': 1}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/preferences/feed/exclusion/delete didn't work.")

    def test_case18(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        insert_feed_publications()

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/preferences/feed/publication/exclusion/create', {'feed_id': 1, 'publication_id': 1},
                               format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/preferences/feed/publication/exclusion/create didn't work.")

    def test_case19(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        insert_feed_publications()

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/preferences/feed/publication/exclusion/create', {'feed_id': 1, 'publication_id': 1},
                               format='json')
        response = client.post('/preferences/feed/publication/exclusion/delete', {'feed_id': 1, 'publication_id': 1},
                               format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         "/preferences/feed/publication/exclusion/delete didn't work.")

    def test_case20(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        insert_feed_publications()

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/preferences/feed/publication/exclusion/all/create', {'feed_id': 1}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "preferences/feed/publication/exclusion/all/create didn't work.")

    def test_case21(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        insert_feed_publications()

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/preferences/feed/publication/exclusion/all/create', {'feed_id': 1}, format='json')
        response = client.post('/preferences/feed/publication/exclusion/all/delete', {'feed_id': 1}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/preferences/feed/publication/exclusion/all/delete didn't work.")

    def test_case22(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/user/language', {'language': 'pt'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, "/user/language didn't work.")

    def test_case23(self):
        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/login/', {'email': email, 'name': name, 'font_size': font_size, 'language': language}, format='json')

        client = APIClient()
        client.credentials(HTTP_FACEBOOKID=facebook_id, HTTP_TOKEN=facebook_token)

        response = client.post('/user/font', {'font_size': 'S'}, format='json')

        self.assertEqual(0, Feed.objects.count(), "It should be zero.")
        self.assertEqual(response.status_code, status.HTTP_200_OK, "/user/font didn't work.")
