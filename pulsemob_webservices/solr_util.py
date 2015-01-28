# coding: utf-8

__author__ = 'jociel'

from xylose.scielodocument import Article
from datetime import datetime
from webservices.webservices.models import Feed, Publication
import re
import django

django.setup()

control_chars = ''.join(map(unichr, range(0, 32) + range(127, 160)))
control_char_re = re.compile('[%s]' % re.escape(control_chars))


def remove_control_chars(s):
    if s is None:
        return ""
    else:
        return control_char_re.sub('', s)


def get_solr_args_from_article(document):
    article = Article(document)

    original_title = article.original_title()
    if original_title is not None:
        original_title = original_title

    try:  # publication_date format maybe yyyy-mm-dd
        publication_date = datetime.strptime(article.publication_date, '%Y-%m-%d').isoformat()
    except ValueError:
        try:  # publication_date format maybe yyyy-mm
            publication_date = datetime.strptime("{0}-01".format(article.publication_date), '%Y-%m-%d').isoformat()
        except ValueError:  # publication_date format maybe yyyy
            publication_date = datetime.strptime("{0}-01-01".format(article.publication_date), '%Y-%m-%d').isoformat()

    article_languages = article.languages()
    languages = []
    for l in article_languages:
        languages.append(l)

    article_authors = article.authors
    authors = []
    if article_authors is not None:
        for author in article_authors:
            author_name = u"{0} {1}".format(author["given_names"], author["surname"])
            authors.append(remove_control_chars(author_name))

    article_first_author = article.first_author
    if article_first_author is not None:
        first_author = remove_control_chars(u"{0} {1}".format(article_first_author["given_names"], article_first_author["surname"]))
    else:
        first_author = ""

    #Start - Insert feed and publication
    print ('Start - Insert feed and publication')

    feeds = list(Feed.objects.all())
    publications = list(Publication.objects.all().prefetch_related('feeds'))
    feed_ids = []
    publication_ids = []
    publication_name = remove_control_chars(u"{0}".format(article.journal.title)).title()

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

    publication_ids.append(publication.id)

    for item_feed in article.journal.subject_areas:
        feed_name = remove_control_chars(u"{0}".format(item_feed)).title()

        feed_exists = False
        feed = None
        for feed_loop in feeds:
            if feed_loop.feed_name_en == feed_name:
                feed_exists = True
                feed = feed_loop
                break

        if not feed_exists:
            feed = Feed(None, feed_name)
            feed.save()
            feeds.append(feed)

        feed_ids.append(feed.id)

        feed_publication_relationship = False
        for feed_loop in publication.feeds.all():
            if feed_loop.feed_name_en == feed_name:
                feed_publication_relationship = True
                break

        if not feed_publication_relationship:
            publication.feeds.add(feed)

    print ('End - Insert feed and publication')
    # End - Insert feed and publication

    args = {
        "id": u"{0}{1}".format(article.publisher_id, article.collection_acronym),
        "scielo_issn": article.journal.scielo_issn,
        "any_issn": article.journal.any_issn(),
        "journal_title": remove_control_chars(article.journal.title),  # publication
        "journal_title_id": publication_ids,

        "journal_abbreviated_title": remove_control_chars(article.journal.abbreviated_title),
        "original_title": remove_control_chars(original_title),
        "original_abstract": remove_control_chars(article.original_abstract()),
        "publication_date": "{0}Z".format(publication_date),
        "journal_acronym": article.journal.acronym,
        "subject_areas": article.journal.subject_areas,  # feed
        "subject_areas_ids": feed_ids,  # feed ids

        "wos_subject_areas": article.journal.wos_subject_areas,

        "original_language": article.original_language(),
        "languages": languages,
        "document_type": article.document_type,
        "authors": authors,
        "first_author": first_author,
        "corporative_authors": article.corporative_authors,
        "scielo_domain": article.scielo_domain,
        "publisher_id": article.publisher_id,
        "collection_acronym": article.collection_acronym
    }

    article_translated_abstracts = article.translated_abstracts()
    if article_translated_abstracts is not None:
        for language in article_translated_abstracts:
            args[u"translated_abstracts_{0}".format(language)] = remove_control_chars(article_translated_abstracts[language])

    article_translated_titles = article.translated_titles()
    if article_translated_titles is not None:
        for language in article_translated_titles:
            args[u"translated_titles_{0}".format(language)] = remove_control_chars(article_translated_titles[language])

    article_keywords = article.keywords()
    if article_keywords is not None:
        for language in article_keywords:
            keywords = []
            for keyword in article_keywords[language]:
                keywords.append(remove_control_chars(keyword))
            args[u"keywords_{0}".format(language)] = keywords

    return args