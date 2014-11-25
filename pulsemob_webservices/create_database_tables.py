__author__ = 'jociel'

import ConfigParser
import psycopg2

if __name__ == '__main__':
    config = ConfigParser.ConfigParser()
    config.read('harvest.cfg')
    data_source_name = config.get("harvest", "data_source_name")

    table_names = {"article_data", "article_data_temp"}

    with psycopg2.connect(data_source_name) as conn:
        with conn.cursor() as curs:
            for table_name in table_names:
                curs.execute('CREATE TABLE {0} ('
                             'id character varying(32), '
                             'action "char", '
                             'hash_code integer)'.format(table_name))
