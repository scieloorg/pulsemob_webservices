__author__ = 'vitor'

from django.http import HttpResponse
from services import memcache_connection
import requests
from pprint import pprint
import ast


class RequestMiddleware(object):
    def process_request(self, request):
        facebook_id = request.META.get('HTTP_FACEBOOKID', None)
        google_id = request.META.get('HTTP_GOOGLEID', None)
        token = request.META.get('HTTP_TOKEN', None)

        mc = memcache_connection()

        if (facebook_id is None and google_id is None) or token is None:
            return HttpResponse('You should provide a facebook id or a google id and a token.', status=400)

        value = mc.get(token)
        if value:
            print ('Token was found in cache.')
            print (value, google_id)
            if google_id is not None and not value == google_id:
                return HttpResponse('This access token is related to another user.', status=401)
            else:
                return None

        print('Token was not found in cache.')

        if facebook_id is not None:
            response = requests.get("https://graph.facebook.com/me", params={'id': facebook_id, 'access_token': token})

            if not response.status_code == 200:
                mc.delete(token)
                return HttpResponse('Error validating facebook token.', status=response.status_code)
            else:
                mc.set(token, facebook_id, 7200)
                print ('Validation ok.')
                return None
        else:
                response = requests.get('https://www.googleapis.com/oauth2/v1/tokeninfo', params={'access_token': token})

                if not response.status_code == 200:
                    mc.delete(token)
                    return HttpResponse('Error validating google token.', status=response.status_code)
                else:
                    json_response = ast.literal_eval(response._content)

                    if not json_response['user_id'] == google_id:
                        return HttpResponse('This access token is related to another user.', status=401)
                    else:
                        mc.set(token, google_id, int(json_response['expires_in']))
                        print ('Validation ok.')
                        return None
