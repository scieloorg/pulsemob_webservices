# coding: utf-8

__author__ = 'jociel'

from xylose.scielodocument import Article
from datetime import datetime
from webservices.models import Magazine, Category
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

    #Start - Insert categories and magazines
    # print ('Start - Insert categories and magazines')

    magazine_name = remove_control_chars(u"{0}".format(article.journal.title))
    magazine_issn = article.journal.scielo_issn
    magazine_abbreviated_title = remove_control_chars(article.journal.abbreviated_title)
    magazine_domain = article.scielo_domain
    magazine_acronym = article.journal.acronym


    try:
        magazine = Magazine.objects.get(magazine_name=magazine_name)
    except Magazine.DoesNotExist:
        magazine = Magazine.objects.create(magazine_name=magazine_name,
                                           magazine_abbreviated_title=magazine_abbreviated_title,
                                           magazine_issn=magazine_issn,
                                           magazine_domain=magazine_domain,
                                           magazine_acronym=magazine_acronym)
        magazine.save()

    category_ids = []
    for item_category in article.journal.subject_areas:
        category_name = remove_control_chars(u"{0}".format(item_category)).title()

        try:
            category = Category.objects.get(category_name_en=category_name)
        except Category.DoesNotExist:
            category = Category.objects.create(category_name_en=category_name)
            category.save()

        category_ids.append(category.id)

        category_publication_relationship = False
        for category_loop in magazine.categories.all():
            if category_loop.category_name_en == category_name:
                category_publication_relationship = True
                break

        if not category_publication_relationship:
            magazine.categories.add(category)
            magazine.save()

    # print ('End - Insert categories and magazines')
    # End - Insert categories and magazines

    args = {
        "id": u"{0}{1}".format(article.publisher_id, article.collection_acronym),
        # "scielo_issn": article.journal.scielo_issn,
        "any_issn": article.journal.any_issn(),
        "journal_title": remove_control_chars(article.journal.title),  # Magazine
        "journal_id": magazine.id,

        "journal_volume": article.volume,
        "journal_number": article.issue,

        # "journal_abbreviated_title": remove_control_chars(article.journal.abbreviated_title),
        "original_title": remove_control_chars(original_title),
        "original_abstract": remove_control_chars(article.original_abstract()),
        "publication_date": "{0}Z".format(publication_date),
        # "journal_acronym": article.journal.acronym,
        "subject_areas": article.journal.subject_areas,  # Categories
        "subject_areas_ids": category_ids,  # Category ids

        "wos_subject_areas": article.journal.wos_subject_areas,

        "original_language": article.original_language(),
        "languages": languages,
        "document_type": article.document_type,
        "authors": authors,
        "first_author": first_author,
        "corporative_authors": article.corporative_authors,
        # "scielo_domain": article.scielo_domain,
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