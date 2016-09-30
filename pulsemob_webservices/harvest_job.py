# coding: utf-8

__author__ = 'jociel'

import logging
import ConfigParser
import solr
from harvest import harvest
import solr_util
import time


def delete_article_entry(code):
    print(code)
    solr_conn.delete(code=code)


def add_update_article_entry(code, document, action, indexed_date):
    try:
        args = solr_util.get_solr_args_from_article(document, indexed_date)
    except Exception as ex:
        logging.exception(ex)

    while True:
        try:
            solr_conn.add(**args)
            break
        except Exception as ex:
            logging.error(
                "An error has occurred trying to access Solr. Arguments passed to Solr and the traceback are below:")
            logging.error(args)
            logging.exception(ex)
            logging.error("Sleeping for 1 minute to try again...")
            time.sleep(60)


if __name__ == '__main__':
    FORMAT = '%(asctime)-15s %(message)s'
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    config = ConfigParser.ConfigParser()
    config.read('harvest.cfg')

    solr_uri = config.get("harvest", "solr_uri")
    solr_conn = solr.SolrConnection(solr_uri)

    harvest(config.get("harvest", "article_meta_uri"),
            "article",
            config.get("harvest", "data_source_name"),
            "article_data",
            config.get("harvest", "pg_shared_folder_output"),
            config.get("harvest", "pg_shared_folder_input"),
            (add_update_article_entry, delete_article_entry)
    )

    solr_conn.commit()