import logging
from django.http import HttpResponse
from services import memcache_connection
import requests
import json
import sys
import hashlib
import jwt_util
from custom_exception import CustomException, CustomErrorMessages

# Get logger.
logger = logging.getLogger(__name__)


class MobileMiddleware(object):
    def process_request(self, request):
        try:
            logger.info('/mobile')
            logger.info('Authenticating user...')
            return None
            print('Authenticating user...')

            # region Getting data from meta.
            facebook_id = request.META.get('HTTP_FACEBOOKID', None)
            google_id = request.META.get('HTTP_GOOGLEID', None)
            token = request.META.get('HTTP_TOKEN', None)
            token_type = request.META.get('HTTP_TOKENTYPE', None)

            if token_type is None:
                token_type = "access_token"

            if facebook_id is None:
                logger.warning("Facebook id was not provided.")

            if google_id is None:
                logger.warning("Google id was not provided.")

            if token is None:
                logger.warning("Token was not provided.")

            if (facebook_id is None and google_id is None) or token is None:
                logger.warning('Authentication failed. A Facebook id or a Google id and a token was not provided.')
                return HttpResponse('You should provide a Facebook id or a Google id and a token.', status=400)

            # endregion

            # region Encoding token.
            user_id = facebook_id if facebook_id is not None else google_id
            hash = hashlib.sha1()
            hash.update(token)
            token_hash = user_id + hash.hexdigest()[:100]
            # endregion

            mc = memcache_connection()
            value = mc.get(token_hash)

            # region Validating token if it was found in cache.
            if value:
                logger.info('Token was found in cache.')

                if (google_id is not None and not value == google_id) or \
                        (facebook_id is not None and not value == facebook_id):
                    logger.warning(
                        'Authentication failed. The provided Facebook access token is related to another user.')
                    return HttpResponse('This access token is related to another user.', status=401)
                else:
                    return None
            # endregion

            logger.info('Token was not found in cache.')

            # region Validating Facebook token.
            if facebook_id is not None:
                logger.info("Validating Facebook token...")
                response = requests.get("https://graph.facebook.com/me",
                                        params={'id': facebook_id, 'access_token': token})

                if not response.status_code == 200:
                    mc.delete(token_hash)
                    logger.warning('Authentication failed. An error occurred while validating Facebook token.')
                    return HttpResponse('Error validating Facebook token.', status=response.status_code)
                else:
                    mc.set(token_hash, facebook_id, 7200)
                    logger.info('Authentication ok.')
                    return None
            # endregion

            # region Validating Google token.
            if google_id is not None:
                logger.info("Validating Google token...")

                response = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo', params={token_type: token})

                if not response.status_code == 200:
                    mc.delete(token_hash)
                    logger.warning('Authentication failed. An error occurred while validating Google token.')
                    return HttpResponse('Error validating Google token.', status=response.status_code)
                else:
                    json_response = json.loads(response._content)

                    if json_response['user_id'] != google_id:
                        logger.warning(
                            'Authentication failed. The provided Google access token is related to another user.')
                        return HttpResponse('This access token is related to another user.', status=401)
                    else:
                        logger.info('Authentication ok.')
                        mc.set(token_hash, google_id, int(json_response['expires_in']))
                        return None

            # endregion
        except:
            logger.critical(traceback.format_exc())
            raise


class BackofficeAuthMiddleware(object):
    def process_request(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None)
            jwt_util.jwt_auth_validate_token(token, raise_exception=True)

            return None
        except CustomException as ce:
            logger.error('Exception while authenticating user. Exception: ' + ce.message)
            return HttpResponse(ce.message, status=10)
        except Exception as e:
            logger.error('Unexpected exception while authenticating user. Exception: ' + str(e))
            return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)