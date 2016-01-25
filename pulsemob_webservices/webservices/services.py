__author__ = 'vitor'

from models import User, UserFavorite, Magazine, Feed, Category
import json
import requests
import memcache
from settings import SOLR_URL, CACHES
from django.http import HttpResponse


# Finds an user by a given email.
def user_find_by_email(email):
    try:
        user = User.objects.get(email=email)
        return user
    except User.DoesNotExist:
        return None


def memcache_connection():
    return memcache.Client([CACHES['default']['LOCATION']], debug=0)


def solr_repository_version():
    mc = memcache_connection()
    version = mc.get('solr_version')

    if not version:
        response = requests.get(SOLR_URL + '/admin/luke', params={'wt': 'json'})
        version = response.json()['index']['version']
        mc.set('solr_version', version)
    return int(version)

#
# def article_find_by_feed_id_and_not_publication_id(feed_id, exclusions_publication_id, q, start=0, rows=50):
#     fq_feed_filter = 'subject_areas_ids: ' + str(feed_id)
#     fq_publication_filter = ''
#
#     if len(exclusions_publication_id) > 0:
#         fq_publication_filter = ' -journal_title_id: (' + str(exclusions_publication_id[0])
#
#     i = 1
#     while i < len(exclusions_publication_id):
#         fq_publication_filter = fq_publication_filter + ' OR ' + str(exclusions_publication_id[i])
#         i += 1
#
#     fq_parameter = fq_feed_filter + ' AND ' + fq_publication_filter + ')'
#
#     response = requests.get(SOLR_URL + 'feed', params={'q': fq_parameter})
#     q.put({'feed_id': feed_id, 'response': response.json()['response']})
#


def article_find_by_feed_id(feed_id, q, start=0, rows=50):
    magazine_ids = list(Magazine.objects.values_list('id', flat=True).filter(feed=feed_id))

    # Test
    fq_magazine_filter = ''

    if len(magazine_ids) > 0:
        fq_magazine_filter = ' journal_id: (' + str(magazine_ids[0])

    i = 1
    while i < len(magazine_ids):
        fq_magazine_filter = fq_magazine_filter + ' OR ' + str(magazine_ids[i])
        i += 1

    fq_magazine_filter += ')'
    # Test

    response = requests.get(SOLR_URL + '/feed', params={'q': fq_magazine_filter})

    json_response = response.json()
    q.put({'feed_id': feed_id, 'response': json_response['response']})


def article_find_by_magazine_id(magazine_id, q, start=0, rows=50):
    fq_magazine_filter = 'journal_id: ' + str(magazine_id)

    response = requests.get(SOLR_URL + '/magazine', params={'q': fq_magazine_filter})

    json_response = response.json()
    q.put({'magazine_id': magazine_id, 'response': json_response['response']})


def article_find_favorite_by_user_id(user_id, start=0, rows=50):
    favorites_article_ids = list(UserFavorite.objects.values_list('article_id', flat=True).filter(user_id=user_id))

    if len(favorites_article_ids) == 0:
        return []

    fq_parameter = 'id: ' + str(favorites_article_ids[0])

    i = 1
    while i < len(favorites_article_ids):
        fq_parameter = fq_parameter + ' OR id: ' + str(favorites_article_ids[i])
        i += 1

    response = requests.get(SOLR_URL + '/feed', params={'q': fq_parameter})

    return response.json()['response']


if __name__ == "__main__":
    journal_id = 1;
    response = requests.get('http://192.168.0.2:8983/solr/pulsemob/' + 'feed', params={'q': 'journal_id:' + journal_id, 'fl': 'scielo_domain, scielo_issn, journal_acronym, journal_abbreviated_title', 'start': 0, 'rows': 1})
    print response;