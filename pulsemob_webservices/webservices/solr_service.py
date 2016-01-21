import solr
import traceback
from pprint import pprint
import json
import logging
from settings import SOLR_URL
from custom_exception import CustomException, CustomErrorMessages

# Get logger.
logger = logging.getLogger(__name__)

conn = solr.SolrConnection(SOLR_URL)
select = solr.SearchHandler(conn, "/select")


def get_article(article_id):
    try:
        response = select.__call__(q="id:" + str(article_id))

        if len(response.results) > 0:
            return response.results[0]

        raise CustomException(CustomErrorMessages.ARTICLE_NOT_FOUND)
    except CustomException as ce:
        raise ce
    except Exception as e:
        logger.error('An exceptions was thrown while getting an article. Exception: ' + str(e))
        raise CustomException(CustomErrorMessages.SOLR_COMMUNICATION_FAILURE)


def add_article(doc):
    try:
        conn.add(**doc)
        conn.commit()
    except Exception as e:
        logger.error('An exceptions was thrown while adding an article. Exception: ' + str(e))
        raise CustomException(CustomErrorMessages.SOLR_COMMUNICATION_FAILURE)


def add_image(cover_article):
    try:
        logger.info('Indexing image_path and image_upload_date.')

        response = select.__call__(q="id:" + str(cover_article.article_id))

        upload_time = cover_article.upload_time

        if len(response.results) > 0:
            doc = response.results[0]

            doc["image_upload_date"] = upload_time

            logger.info(doc["id"])
            logger.info(type(doc))

            response = conn.add(**doc)
            conn.commit()

        logger.info('Fields image_path and image_upload_date successfully indexed.')
        logger.info(response)
    except:
        logger.info('An exception was thrown while indexing image_path and image_upload_date.')
        logger.critical(traceback.format_exc())


def remove_image(article_id):
    try:
        logger.info('Deleting image_path and image_upload_date.')

        response = select.__call__(q="id:" + str(article_id))

        if len(response.results) > 0:
            doc = response.results[0]

            doc["image_upload_date"] = None

            logger.info(doc["id"])
            logger.info(type(doc))

            response = conn.add(**doc)
            conn.commit()

        logger.info('Fields image_path and image_upload_date successfully deleted.')
        logger.info(response)
    except Exception as e:
        logger.error('An exception was thrown while deleting image_path and image_upload_date. Exception: ' + str(e))
        raise CustomException(CustomErrorMessages.SOLR_COMMUNICATION_FAILURE)
