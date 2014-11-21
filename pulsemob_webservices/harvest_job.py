# coding: utf-8

__author__ = 'jociel'

import ConfigParser
import solr
from pulsemob_webservices import solr_util
from pulsemob_webservices.harvest import harvest


def delete_article_entry(code):
    solr_conn.delete(code=code)


def add_update_article_entry(code, document, action):
    args = solr_util.get_solr_args_from_article(document)
    solr_conn.add(**args)

if __name__ == '__main__':
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