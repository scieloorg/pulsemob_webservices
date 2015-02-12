__author__ = 'vitor'

from models import User, UserFavorite,UserFeedExclusion, UserPublicationFeedExclusion, Publication, Feed
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


def user_get_general_state(user_id):
    response = dict()
    response['user'] = User.objects.get(id=user_id).to_dict()

    # User favorites information
    user_favorites = UserFavorite.objects.filter(user_id=user_id)
    user_favorites_serialized = []
    for user_favorite in user_favorites:
        user_favorites_serialized.append(user_favorite.article_id)

    response['user_favorites'] = user_favorites_serialized

    # User feed exclusion information
    user_feed_exclusions = UserFeedExclusion.objects.filter(user_id=user_id)

    user_feed_exclusions_serialized = []
    for user_feed_exclusion in user_feed_exclusions:
        user_feed_exclusions_serialized.append({'feed_id': user_feed_exclusion.feed_id})

    response['user_feed_exclusions'] = user_feed_exclusions_serialized

    # User feed publication information
    user_feed_publication_exclusions = UserPublicationFeedExclusion.objects.filter(user_id=user_id)
    user_feed_publication_exclusions_serialized = []
    for user_feed_publication_exclusion in user_feed_publication_exclusions:
        user_feed_publication_exclusions_serialized.append(
            {'feed_id': user_feed_publication_exclusion.feed_id,
             'publication_id': user_feed_publication_exclusion.publication_id})

    response['user_feed_publication_exclusions'] = user_feed_publication_exclusions_serialized

    feeds = Feed.objects.all()
    feeds_serialized = []
    for feed in feeds:
        publication_ids = list(Publication.objects.values_list('id', flat=True).filter(feeds=feed.id))

        feed_dict = feed.to_dict()
        feed_dict['publications'] = publication_ids
        feeds_serialized.append(feed_dict)

    response['feeds'] = feeds_serialized

    publications = list(Publication.objects.all())
    publications_serialized = []
    for publication in publications:
        publications_serialized.append(publication.to_dict())

    response['publications'] = publications_serialized

    return response


def feed_find_all(self):
    #return Feed.objects.all()
    result_list = list(Feed.objects.all().values('id', 'feed_name'))
    return HttpResponse(json.dumps(result_list), content_type="application/json")


def feed_find_by_id(self, id = 1000):
    feed = Feed.objects.get(id=id)
    return HttpResponse(json.dumps(feed.to_dict()), content_type="application/json")
    #response = {"id": feed.id, "feed_name": feed.feed_name}
    #return HttpResponse(json.dumps(response), content_type="application/json")


def memcache_connection():
    print(CACHES['default']['LOCATION'])
    return memcache.Client([CACHES['default']['LOCATION']], debug=0)


def solr_repository_version():
    mc = memcache_connection()
    version = mc.get('solr_version')

    if not version:
        response = requests.get(SOLR_URL + 'admin/luke', params={'wt': 'json'})
        version = response.json()['index']['version']
        mc.set('solr_version', version)
    return int(version)


def article_find_by_feed_id_and_not_publication_id(feed_id, exclusions_publication_id, q, start=0, rows=50):
    fq_feed_filter = 'subject_areas_ids: ' + str(feed_id)

    fq_publication_filter = ''

    if len(exclusions_publication_id) > 0:
        fq_publication_filter = ' -journal_title_id: ' + str(exclusions_publication_id[0])

    i = 1
    while i < len(exclusions_publication_id):
        fq_publication_filter = fq_publication_filter + ' AND -journal_title_id: ' + str(exclusions_publication_id[i])
        i += 1

    fq_parameter = fq_feed_filter + ' AND ' + fq_publication_filter

    response = requests.get(SOLR_URL + 'feed', params={'q': fq_parameter})

    q.put({'feed_id': feed_id, 'response': response.json()['response']})


def article_find_by_feed_id(feed_id, q, start=0, rows=50):
    fq_parameter = 'subject_areas_ids: ' + str(feed_id)

    response = requests.get(SOLR_URL + 'feed', params={'q': fq_parameter})

    json_response = response.json()
    q.put({'feed_id': feed_id, 'response': json_response['response']})


def article_find_favorite_by_user_id(user_id, start=0, rows=50):
    favorites_article_ids = list(UserFavorite.objects.values_list('article_id', flat=True).filter(user_id=user_id))

    if len(favorites_article_ids) == 0:
        return []

    fq_parameter = 'id: ' + str(favorites_article_ids[0])

    i = 1
    while i < len(favorites_article_ids):
        fq_parameter = fq_parameter + ' OR id: ' + str(favorites_article_ids[i])
        i += 1

    response = requests.get(SOLR_URL + 'feed', params={'q': fq_parameter})

    return response.json()['response']


def publication_dictionary(self):
    publications = Publication.objects.all()
    dictionary = {}
    for publication in publications:
        feeds = publication.feeds.all()
        print(feeds.filter(id=1).count())
        dictionary[publication.publication_name] = {'id': publication.id, 'publication_name': publication.publication_name, 'feeds': list(publication.feeds.all().values('id'))}
    return HttpResponse(json.dumps(dictionary), content_type="application/json")


def execute(self, feed_name='Feed 1', publication_name='Publication 1'):
    feeds = list(Feed.objects.all())
    publications = list(Publication.objects.all().prefetch_related('feeds'))

    feed_exists = False
    feed = None
    for feed_loop in feeds:
        if feed_loop.feed_name == feed_name:
            feed_exists = True
            feed = feed_loop
            break

    if not feed_exists:
        feed = Feed(None, feed_name)
        feed.save()
        feeds.append(feed)

    publication_exists = False
    publication = None
    for publication_loop in publications:
        if publication_loop.publication_name == publication_name:
            publication_exists = True
            publication = publication_loop
            break

    if not publication_exists:
        publication = Publication(None, publication_name)
        publication.save()
        publications.append(publication)

    feed_publication_relationship = False
    for feed_loop in publication.feeds.all():
        if feed_loop.feed_name == feed_name:
            feed_publication_relationship = True
            break

    if not feed_publication_relationship:
        publication.feeds.add(feed)

    #Second turn
    feed_name = 'Feed 2'

    feed_exists = False
    feed = None
    for feed_loop in feeds:
        if feed_loop.feed_name == feed_name:
            feed_exists = True
            feed = feed_loop
            break

    if not feed_exists:
        feed = Feed(None, feed_name)
        feed.save()
        feeds.append(feed)

    publication_exists = False
    publication = None
    for publication_loop in publications:
        if publication_loop.publication_name == publication_name:
            publication_exists = True
            publication = publication_loop
            break

    if not publication_exists:
        publication = Publication(None, publication_name)
        publication.save()
        publications.append(publication)

    feed_publication_relationship = False
    for feed_loop in publication.feeds.all():
        if feed_loop.feed_name == feed_name:
            feed_publication_relationship = True
            break

    if not feed_publication_relationship:
        publication.feeds.add(feed)

    return HttpResponse(json.dumps(''), content_type="application/json")