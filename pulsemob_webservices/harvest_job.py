# coding: utf-8

__author__ = 'jociel'

import requests
import psycopg2
import solr
import os
import ConfigParser
from xylose.scielodocument import Article, Journal

def do_request(url, params):
    response = requests.get(url, params=params).json()

    return response

def extract_data_from_article_webservice_to_file(article_meta_uri, output_filepath, page_limit=None):
    with open(output_filepath, "w") as text_file:
        page = 0
        while True:
            print 'Extracting articles from webservice (page {0})...'.format(page)
            params = {'offset': page*1000}
            identifiers = do_request(
                '{0}/article/identifiers'.format(article_meta_uri),
                params
            )
            documents = identifiers['objects']
            if len(documents) == 0 or (page_limit is not None and page > page_limit):
                break
            for identifier in documents:
                code = identifier['code']
                hash_code = identifier['processing_date'].replace("-", "")
                text_file.write("{0},{1},{2}\n".format(code, "", hash_code))

            page += 1

def extract_data_from_journal_webservice_to_file(article_meta_uri, output_filepath):
    print 'Extracting journals from webservice...'
    with open(output_filepath, "w") as text_file:
        documents = do_request(
            '{0}/{1}'.format(article_meta_uri, 'journal'),
            {}
        )
        for document in documents:
            journal = Journal(document)
            hash_code = hash(str(document))
            text_file.write("{0},{1},{2}\n".format(journal.scielo_issn, "", hash_code))

def store_and_process_data_from_file(curs, input_filepath, data_table, temp_table):
    curs.execute("COPY {0} FROM '{1}' USING DELIMITERS ',' CSV".format(temp_table, input_filepath))
    curs.execute("UPDATE {0} a SET action='D' WHERE NOT EXISTS (SELECT 1 FROM {1} WHERE id = a.id)".format(data_table, temp_table))
    curs.execute("UPDATE {0} a SET action='I' WHERE NOT EXISTS (SELECT 1 FROM {1} WHERE id = a.id)".format(temp_table, data_table))
    curs.execute("UPDATE {0} a SET action='U' WHERE EXISTS (SELECT 1 FROM {1} WHERE id = a.id AND hash_code != a.hash_code)".format(temp_table, data_table))

def delete_entries_from_solr(curs, table_name, solr_conn):
    curs.execute("SELECT id FROM {0} WHERE action = 'D'".format(table_name))
    rows = curs.fetchall()
    for row in rows:
        print "removing entry '{0}' from solr...".format(row[0])
        # solr_conn.delete(row[0])
        # solr_conn.commit()

def add_article_to_solr(solr_conn, document):
    article = Article(document)
    id = article.publisher_id
    publisher_name = article.journal.publisher_name
    title = article.original_title()
    article.keywords()

    print "adding article '{0}' to solr...".format(title.encode("utf-8"))
    # solr_conn.add(id=id,
    #               title=title,
    #               publisher_name=publisher_name)
    # solr_conn.commit()

def add_journal_to_solr(solr_conn, document):
    journal = Journal(document)
    id = journal.scielo_issn
    publisher_name = journal.publisher_name
    title = journal.title
    print "adding journal '{0}' to solr...".format(id)
    # solr_conn.add(id=id,
    #               title=title,
    #               publisher_name=publisher_name)
    # solr_conn.commit()

def add_entries_to_solr(curs, table_name, solr_conn, article_meta_uri, endpoint):
    if endpoint == 'article':
        key = 'code'
        add_to_solr_method = add_article_to_solr
    elif endpoint == 'journal':
        key = 'issn'
        add_to_solr_method = add_journal_to_solr
    curs.execute("SELECT id FROM {0} WHERE action = 'I'".format(table_name))
    rows = curs.fetchall()
    for row in rows:
        id = row[0]
        dparams = {}
        dparams[key] = id
        document = do_request(
            '{0}/{1}'.format(article_meta_uri, endpoint), dparams
        )
        if isinstance(document, dict):
            doc_ret = document
        elif isinstance(document, list):
            if len(document) > 0:
                doc_ret = document[0]
            else:
                doc_ret = None

        if doc_ret != None:
            add_to_solr_method(solr_conn, doc_ret)
        else:
            print "{0} '{1}' not found.".format(endpoint, id)

def switch_and_clean_tables(curs, endpoint):
    curs.execute("ALTER TABLE {0}_data_temp RENAME TO {0}_data_temp_temp".format(endpoint))
    curs.execute("ALTER TABLE {0}_data RENAME TO {0}_data_temp".format(endpoint))
    curs.execute("ALTER TABLE {0}_data_temp_temp RENAME TO {0}_data".format(endpoint))
    curs.execute("TRUNCATE {0}_data_temp".format(endpoint))
    curs.execute("UPDATE {0}_data SET action = NULL".format(endpoint))

def harvest(article_meta_uri, endpoint, data_source_name, data_table_name, pg_shared_folder_output, pg_shared_folder_input, solr_uri):
    output_file = "{0}/{1}.txt".format(pg_shared_folder_output, data_table_name)
    input_file = "{0}/{1}.txt".format(pg_shared_folder_input, data_table_name)
    if endpoint == 'article':
        extract_data_from_article_webservice_to_file(article_meta_uri, output_file)
    elif endpoint == 'journal':
        extract_data_from_journal_webservice_to_file(article_meta_uri, output_file)
    else:
        raise Exception('Invalid Endpoint: {0}'.format(endpoint))
    with psycopg2.connect(data_source_name) as conn:
        with conn.cursor() as curs:
            temp_table = "{0}_temp".format(data_table_name)
            store_and_process_data_from_file(curs, input_file, data_table_name, temp_table)
        with conn.cursor() as curs:
            solr_conn = solr.SolrConnection(solr_uri)
            delete_entries_from_solr(curs, data_table_name, solr_conn)
            add_entries_to_solr(curs, temp_table, solr_conn, article_meta_uri, endpoint)
        with conn.cursor() as curs:
            switch_and_clean_tables(curs, endpoint)

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read('harvest.cfg')
    harvest(config.get("harvest", "article_meta_uri"),
            "article",
            config.get("harvest", "data_source_name"),
            "article_data",
            config.get("harvest", "pg_shared_folder_output"),
            config.get("harvest", "pg_shared_folder_input"),
            config.get("harvest", "solr_uri")
            )