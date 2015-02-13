__author__ = 'vitor'

import logging
from django.http import HttpResponse
from services import memcache_connection
import requests
import ast
import sys

logger = logging.getLogger(__name__)


class RequestMiddleware(object):
    def process_request(self, request):
        try:
            logger.info ('AUTHENTICATION - Authenticating user...')
            facebook_id = request.META.get('HTTP_FACEBOOKID', None)
            google_id = request.META.get('HTTP_GOOGLEID', None)
            token = request.META.get('HTTP_TOKEN', None)

            if facebook_id is None:
                logger.info("AUTHENTICATION - Facebook id was not provided.")
            else:
                logger.info("AUTHENTICATION - Facebook id was provided.")

            if google_id is None:
                logger.info("AUTHENTICATION - Google id was not provided.")
            else:
                logger.info("AUTHENTICATION - Google id was provided.")

            if token is None:
                logger.info("AUTHENTICATION - Token was not provided.")
            else:
                logger.info("AUTHENTICATION - Token was provided.")

            mc = memcache_connection()

            if (facebook_id is None and google_id is None) or token is None:
                return HttpResponse('You should provide a facebook id or a google id and a token.', status=400)

            value = mc.get(token)
            if value:
                logger.info ('AUTHENTICATION - Token was found in cache.')
                if (google_id is not None and not value == google_id) or \
                        (facebook_id is not None and not value == facebook_id):
                    logger.info('AUTHENTICATION - Authentication not ok.')
                    return HttpResponse('This access token is related to another user.', status=401)
                else:
                    return None

            logger.info('AUTHENTICATION - Token was not found in cache.')

            if facebook_id is not None:
                logger.info("AUTHENTICATION - Authenticating facebook user.")
                response = requests.get("https://graph.facebook.com/me", params={'id': facebook_id, 'access_token': token})

                if not response.status_code == 200:
                    mc.delete(token)
                    logger.info ('AUTHENTICATION - Authentication not ok.')
                    return HttpResponse('Error validating facebook token.', status=response.status_code)
                else:
                    mc.set(token, facebook_id, 7200)
                    logger.info ('AUTHENTICATION - Authentication ok.')
                    return None
            else:
                logger.info("AUTHENTICATION - Authenticating google user.")
                response = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo', params={'access_token': token})

                if not response.status_code == 200:
                    mc.delete(token)
                    logger.info ('AUTHENTICATION - Authentication not ok.')
                    return HttpResponse('Error validating google token.', status=response.status_code)
                else:
                    json_response = ast.literal_eval(response._content)

                    if not json_response['user_id'] == google_id:
                        logger.info ('AUTHENTICATION - Authentication not ok.')
                        return HttpResponse('This access token is related to another user.', status=401)
                    else:
                        logger.info ('AUTHENTICATION - Authentication ok.')
                        mc.set(token, google_id, int(json_response['expires_in']))
                        return None
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise