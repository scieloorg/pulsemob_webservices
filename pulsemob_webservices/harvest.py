# coding: utf-8
import time
import traceback
import solr

__author__ = 'jociel'

import requests
import psycopg2
from xylose.scielodocument import Journal, Article
import solr_util


def do_request(url, params):
    while True:
        try:
            response = requests.get(url, params=params).json()
            break
        except Exception as ex:
            print "An error has occurred trying to do an url request. " \
                  "The used url and parameters and the traceback are below:"
            print url
            print params
            traceback.print_exc()
            print "Sleeping for 1 minute to try again..."
            time.sleep(60)

    return response


def extract_data_from_article_webservice_to_file(article_meta_uri, output_filepath, page_limit=None):
    with open(output_filepath, "w") as text_file:
        page = 0
        while True:
            if page_limit is not None and page >= page_limit:
                break
            print '{0} - Extracting articles from webservice (page {1})...'.format(time.ctime(), page)
            params = {'offset': page*1000}
            identifiers = do_request(
                '{0}/article/identifiers'.format(article_meta_uri),
                params
            )
            documents = identifiers['objects']
            if len(documents) == 0:
                break
            for identifier in documents:
                code = identifier['code']
                hash_code = identifier['processing_date'].replace("-", "")
                text_file.write("{0},{1},{2}\n".format(code, "", hash_code))

            page += 1


def extract_data_from_journal_webservice_to_file(article_meta_uri, output_filepath):
    print '{0} - Extracting journals from webservice...'.format(time.ctime())
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
    print "{0} - Processing data...".format(time.ctime())
    curs.execute("TRUNCATE {0}".format(temp_table))
    curs.execute("COPY {0} FROM '{1}' USING DELIMITERS ',' CSV".format(temp_table, input_filepath))
    curs.execute("UPDATE {0} a SET action='D' WHERE NOT EXISTS (SELECT 1 FROM {1} WHERE id = a.id)".format(data_table, temp_table))
    curs.execute("UPDATE {0} a SET action='I' WHERE NOT EXISTS (SELECT 1 FROM {1} WHERE id = a.id)".format(temp_table, data_table))
    curs.execute("UPDATE {0} a SET action='U' WHERE EXISTS (SELECT 1 FROM {1} WHERE id = a.id AND hash_code != a.hash_code)".format(temp_table, data_table))


def delete_entries(curs, table_name, delete_entry_method):
    print "{0} - Deleting entries...".format(time.ctime())
    curs.execute("SELECT id FROM {0} WHERE action = 'D'".format(table_name))
    rows = curs.fetchall()
    for row in rows:
        delete_entry_method(row[0])

    print "{0} - {1} entries deleted.".format(time.ctime(), len(rows))


def add_update_entries(curs, table_name, article_meta_uri, endpoint, add_update_entry_method, action):
    if action == "I":
        print "{0} - Adding entries...".format(time.ctime())
    elif action == "U":
        print "{0} - Updating entries...".format(time.ctime())

    if endpoint == 'article':
        key = 'code'
    elif endpoint == 'journal':
        key = 'issn'

    curs.execute("SELECT id FROM {0} WHERE action = '{1}'".format(table_name, action))
    rows = curs.fetchall()
    for r, row in enumerate(rows):
        code = row[0]
        dparams = {key: code}
        document = do_request(
            '{0}/{1}'.format(article_meta_uri, endpoint), dparams
        )
        if document is None:
            doc_ret = None
        if isinstance(document, dict):
            doc_ret = document
        elif isinstance(document, list):
            if len(document) > 0:
                doc_ret = document[0]
            else:
                doc_ret = None

        if doc_ret is not None:
            add_update_entry_method(code, doc_ret, action)
        else:
            print "{0} '{1}' not found.".format(endpoint, code)

        if r != 0 and r % 100 == 0:
            if action == "I":
                print "{0} - {1} entries added... continuing...".format(time.ctime(), r)
            elif action == "U":
                print "{0} - {1} entries updated... continuing...".format(time.ctime(), r)

    if action == "I":
        print "{0} - {1} entries added.".format(time.ctime(), len(rows))
    elif action == "U":
        print "{0} - {1} entries updated.".format(time.ctime(), len(rows))


def switch_and_clean_tables(curs, data_table_name, temp_table):
    curs.execute("ALTER TABLE {0} RENAME TO {0}_temp".format(temp_table))
    curs.execute("ALTER TABLE {0} RENAME TO {1}".format(data_table_name, temp_table))
    curs.execute("ALTER TABLE {0}_temp RENAME TO {1}".format(temp_table, data_table_name))
    curs.execute("UPDATE {0} SET action = NULL".format(data_table_name))
    curs.execute("TRUNCATE {0}".format(temp_table))


def harvest(article_meta_uri,
            endpoint,
            data_source_name,
            data_table_name,
            pg_shared_folder_output,
            pg_shared_folder_input,
            process_entry_methods):
    (add_update_entry, delete_entry) = process_entry_methods
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
            delete_entries(curs, data_table_name, delete_entry)
            add_update_entries(curs, temp_table, article_meta_uri, endpoint, add_update_entry, "I")
            add_update_entries(curs, temp_table, article_meta_uri, endpoint, add_update_entry, "U")
            switch_and_clean_tables(curs, data_table_name, temp_table)
        conn.commit()
    print "{0} - Process finished.".format(time.ctime())


if __name__ == '__main__':
    code = "S0718-34372014000100009"
    dparams = {"code": code}
    document = do_request(
        "http://articlemeta.scielo.org/api/v1/article", dparams
    )
    if document is None:
        doc_ret = None
    if isinstance(document, dict):
        doc_ret = document
    elif isinstance(document, list):
        if len(document) > 0:
            doc_ret = document[0]
        else:
            doc_ret = None

    article = Article(doc_ret)
    print article.translated_abstracts()
    args = solr_util.get_solr_args_from_article(doc_ret)
    print args
    solr_uri = "http://192.168.0.2:8983/solr/pulsemob_solr"
    solr_conn = solr.SolrConnection(solr_uri)
    solr_conn.add(**args)

