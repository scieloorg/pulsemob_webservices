# coding: utf-8

__author__ = 'jociel'

from xylose.scielodocument import Article
from datetime import datetime
import re

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
            author_name = "{0} {1}".format(author["given_names"].encode('utf-8'), author["surname"].encode('utf-8'))
            authors.append(remove_control_chars(author_name.decode('utf-8')))

    article_first_author = article.first_author
    if article_first_author is not None:
        first_author = remove_control_chars("{0} {1}".format(article_first_author["given_names"].encode('utf-8'), article_first_author["surname"].encode('utf-8')).decode('utf-8'))
    else:
        first_author = ""

    args = {
        "id": article.publisher_id,
        "code": article.publisher_id,
        "scielo_issn": article.journal.scielo_issn,
        "any_issn": article.journal.any_issn(),
        "journal_title": remove_control_chars(article.journal.title),
        "journal_abbreviated_title": remove_control_chars(article.journal.abbreviated_title),
        "original_title": remove_control_chars(original_title),
        "original_abstract": remove_control_chars(article.original_abstract()),
        "publication_date": "{0}Z".format(publication_date),
        "journal_acronym": article.journal.acronym,
        "subject_areas": article.journal.subject_areas,
        "wos_subject_areas": article.journal.wos_subject_areas,
        "original_language": article.original_language(),
        "languages": languages,
        "document_type": article.document_type,
        "authors": authors,
        "first_author": first_author,
        "corporative_authors": article.corporative_authors,
        "scielo_domain": article.scielo_domain,
        "publisher_id": article.publisher_id
    }

    article_translated_abstracts = article.translated_abstracts()
    if article_translated_abstracts is not None:
        for language in article_translated_abstracts:
            args["translated_abstracts_{0}".format(language)] = remove_control_chars(article_translated_abstracts[language])

    article_translated_titles = article.translated_titles()
    if article_translated_titles is not None:
        for language in article_translated_titles:
            args["translated_titles_{0}".format(language)] = remove_control_chars(article_translated_titles[language])

    article_keywords = article.keywords()
    if article_keywords is not None:
        for language in article_keywords:
            keywords = []
            for keyword in article_keywords[language]:
                keywords.append(remove_control_chars(keyword))
            args["keywords_{0}".format(language)] = keywords

    return args