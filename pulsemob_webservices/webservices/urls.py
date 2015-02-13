from django.conf.urls import url
from views import *

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^login', login),
    url(r'^home', home),

    url(r'^solr/version', solr_version),

    url(r'^favorite/create', create_favorite),
    url(r'^favorite/read', read_favorite),
    url(r'^favorite/delete', delete_favorite),

    url(r'^feed/publications/list', list_feed_publications),

    url(r'^preferences/feed/exclusion/create', create_feed_exclusion),
    url(r'^preferences/feed/exclusion/delete', delete_feed_exclusion),

    url(r'^preferences/feed/publication/exclusion/create', create_feed_publication_exclusion),
    url(r'^preferences/feed/publication/exclusion/delete', delete_feed_publication_exclusion),
    url(r'^preferences/feed/publication/exclusion/all/create', create_feed_publication_exclusion_all),
    url(r'^preferences/feed/publication/exclusion/all/delete', delete_feed_publication_exclusion_all),

    url(r'^user/language', user_change_language),
    url(r'^user/font', user_change_font_size),
]