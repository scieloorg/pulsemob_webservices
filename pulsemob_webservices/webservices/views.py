# encoding=utf8
__author__ = 'cadu'

from models import Feed, Magazine, Category, User, UserFavorite, Administrator, CoverArticle, PROFILE_OPTIONS
from serializers import AdministratorSerializer, MagazineSerializer, CategorySerializer, CoverArticleSerializer
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, MultiPartParser, FileUploadParser
from django.utils.decorators import decorator_from_middleware
from django.utils.six import BytesIO
from django.core import serializers
from django.core.files.storage import default_storage
from django.db import transaction
from middleware import BackofficeAuthMiddleware, MobileMiddleware
import solr_service
import pprint
import json
import Queue
import threading
import thread
import sys
import services
import traceback
import settings
import logging
import uuid
import jwt_util
from custom_exception import CustomException, CustomErrorMessages
import validator
import email_sender
import bcrypt

# Get logger.
logger = logging.getLogger(__name__)


# region Mobile.
def get_user_by_header_request(request):
    facebook_id = request.META.get('HTTP_FACEBOOKID', None)
    google_id = request.META.get('HTTP_GOOGLEID', None)

    if facebook_id is not None:
        try:
            user = User.objects.get(facebook_id=facebook_id)
            return user
        except User.DoesNotExist:
            pass
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    else:
        try:
            user = User.objects.get(google_id=google_id)
            return user
        except User.DoesNotExist:
            pass
        except:
            logger.critical(traceback.format_exc())
            raise


@decorator_from_middleware(MobileMiddleware)
def login_mobile(self):
    try:
        logger.info('Handling /login.')

        if self.method == 'POST':
            data = json.loads(self.body)
            email = data.get('email', None)
            name = data.get('name', None)
            language = data.get('language', None)
            font_size = data.get('font_size', None)

            facebook_id = self.META.get('HTTP_FACEBOOKID', None)
            google_id = self.META.get('HTTP_GOOGLEID', None)

            # Try get by email. If user was not found, user = None for now.
            if email is not None:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = None

            # If email or user is None, try to get by social id.
            if email is None or user is None:
                if facebook_id is not None:
                    try:
                        user = User.objects.get(facebook_id=facebook_id)
                    except User.DoesNotExist:
                        user = None
                elif google_id is not None:
                    try:
                        user = User.objects.get(google_id=google_id)
                    except User.DoesNotExist:
                        user = None

            if user is None:
                user = User(email=email, name=name, facebook_id=facebook_id, google_id=google_id, language=language,
                            font_size=font_size)
                user.save()
            else:
                if user.facebook_id is None and facebook_id is not None:
                    user.facebook_id = facebook_id
                    user.save()
                elif user.google_id is None and google_id is not None:
                    user.google_id = google_id
                    user.save()

            response = dict()
            response['user'] = user.to_dict()
            response['solr_version'] = services.solr_repository_version()

            response["feeds"] = dict();

            feeds = Feed.objects.filter(user=user.id)
            for feed in feeds:
                feed_response = dict()
                feed_response["feed_name"] = feed.feed_name
                feed_response["magazines"] = list(
                    Magazine.objects.order_by('magazine_name').values_list('id', flat=True).filter(feed=feed))

                response["feeds"][feed.id] = feed_response

            response['favorites'] = list(UserFavorite.objects.values_list('article_id', flat=True).filter(user=user))

            return HttpResponse(json.dumps(response), status=200, content_type="application/json")
        else:
            return HttpResponse('', status=405)
    except:
        logger.critical(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


@decorator_from_middleware(MobileMiddleware)
def home(self):
    try:
        logger.info('Handling /home.')

        if self.method == 'GET':
            user = get_user_by_header_request(self)
            user_id = user.id

            feed_ids = list(Feed.objects.filter(user=user_id).values_list('id', flat=True))

            magazine_ids = set()

            for feed_id in feed_ids:
                magazines = list(
                    Magazine.objects.filter(feeds=feed_id).order_by('magazine_name').values_list('id', flat=True))
                i = 0
                for magazine_id in magazines:
                    if i < 3:
                        magazine_ids.add(magazine_id)
                        i += 1
                    else:
                        break

            q = Queue.Queue()

            count_calls = 0
            for magazine_id in magazine_ids:
                count_calls += 1

                t = threading.Thread(target=services.article_find_by_magazine_id, args=(magazine_id, q))

                t.daemon = True
                t.start()

            response = dict()

            i = 0
            while i < count_calls:
                s = q.get()
                response[s['magazine_id']] = s['response']
                i += 1

            return HttpResponse(json.dumps(response), status=200, content_type="application/json")
        else:
            return HttpResponse('', status=405)
    except:
        logger.critical(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


@decorator_from_middleware(MobileMiddleware)
def read_favorite(self):
    logger.info('Handling /favorite/read.')
    try:
        if self.method == 'GET':
            user = get_user_by_header_request(self)
            user_id = user.id

            response = services.article_find_favorite_by_user_id(user_id)
            return HttpResponse(json.dumps(response), status=200)
        else:
            return HttpResponse(status=405)
    except:
        logger.critical(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


@decorator_from_middleware(MobileMiddleware)
def create_favorite(self):
    logger.info('Handling /favorite/create.')
    try:
        if self.method == 'POST':
            user = get_user_by_header_request(self)
            user_id = user.id
            data = json.loads(self.body)
            article_id = data.get('article_id', None)

            if article_id is None:
                return HttpResponse('You should provide article_id parameter.', status=400)

            try:
                UserFavorite.objects.get(user_id=user_id, article_id=article_id)
            except UserFavorite.DoesNotExist:
                user_favorite = UserFavorite(None, user_id, article_id)
                user_favorite.save()

            return HttpResponse(json.dumps({}), status=200)
        else:
            return HttpResponse(status=405)
    except:
        logger.critical(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)



@decorator_from_middleware(MobileMiddleware)
def delete_favorite(self):
    logger.info('Handling /favorite/delete.')
    try:
        if self.method == 'POST':
            user = get_user_by_header_request(self)
            user_id = user.id
            data = json.loads(self.body)
            article_id = data.get('article_id', None)

            try:
                user_favorite = UserFavorite.objects.get(user_id=user_id, article_id=article_id)
                user_favorite.delete()
            except UserFavorite.DoesNotExist:
                pass

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=405)
    except:
        logger.critical(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


@decorator_from_middleware(MobileMiddleware)
def search(self):
    logger.info('Handling /magazine/search.')
    try:
        if self.method == 'POST':
            data = json.loads(self.body)
            text_search = data.get('q', '')

            magazines = list(Magazine.objects.filter(magazine_name__icontains=text_search)
                             .order_by('magazine_name').values_list('id', flat=True))

            return HttpResponse(json.dumps(magazines), status=200)
        else:
            return HttpResponse('', status=405)
    except:
        logger.critical(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


@decorator_from_middleware(MobileMiddleware)
@transaction.atomic
def create_feed(self):
    logger.info('Handling /feed/create.')
    try:
        if self.method == 'POST':
            with transaction.atomic():
                user = get_user_by_header_request(self)
                user_id = user.id

                data = json.loads(self.body)

                feed_name = data.get('feed_name', None)
                magazine_ids = data.get('magazines', None)

                if feed_name is None or magazine_ids is None:
                    return HttpResponse('You should provide feed_name and magazines parameters.', status=400)

                try:
                    Feed.objects.get(user=user_id, feed_name=feed_name)

                    return HttpResponse('Already exists a feed with this name.', status=400)
                except Feed.DoesNotExist:
                    feed = Feed(None, feed_name, user_id)

                    feed.save()

                    for magazine_id in magazine_ids:
                        magazine = Magazine.objects.get(id=magazine_id)
                        feed.magazines.add(magazine);

                    feed.save()

                    response = dict()
                    response["feed_id"] = feed.id
                    response["feed_name"] = feed.feed_name
                    response["magazines"] = list(
                        Magazine.objects.filter(feeds=feed.id).order_by('magazine_name').values_list('id', flat=True))

                return HttpResponse(json.dumps(response), status=200)
        else:
            return HttpResponse('', status=405)
    except:
        logger.critical(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)



@decorator_from_middleware(MobileMiddleware)
def update_feed(self):
    logger.info('Handling /feed/update.')
    try:
        if self.method == 'POST':
            user = get_user_by_header_request(self)

            data = json.loads(self.body)

            feed_id = data.get('feed_id', None)
            add = data.get('add', None)
            remove = data.get('remove', None)

            if feed_id is None or add is None or remove is None:
                return HttpResponse('You should provide feed_id, add and remove parameters.', status=400)

            feed = Feed.objects.get(id=feed_id)

            if feed.user.id != user.id:
                return HttpResponse('You don\'t have permission to change this resource.', status=403)

            for magazine_id in add:
                feed.magazines.add(magazine_id)

            for magazine_id in remove:
                feed.magazines.remove(magazine_id)

            feed.save()

            response = dict()
            response["feed_id"] = feed.id
            response["feed_name"] = feed.feed_name
            response["magazines"] = list(
                Magazine.objects.filter(feeds=feed.id).order_by('magazine_name').values_list('id', flat=True))

            return HttpResponse(json.dumps(response), status=200)
        else:
            return HttpResponse('', status=405)
    except:
        logger.critical(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)



@decorator_from_middleware(MobileMiddleware)
def delete_feed(self):
    logger.info('Handling /feed/delete.')
    if self.method == 'POST':
        try:
            user = get_user_by_header_request(self)
            data = json.loads(self.body)

            feed_id = data.get('feed_id', None)

            feed = Feed.objects.get(id=feed_id)

            if feed.user.id != user.id:
                return HttpResponse('You don\'t have permission to change this resource.', status=403)

            feed.delete()

            return HttpResponse(json.dumps({}), status=200)
        except:
            print "Unexpected error:", sys.exc_info()[0]
    else:
        return HttpResponse('', status=405)


@decorator_from_middleware(MobileMiddleware)
def read_user(self):
    if self.method == 'GET':
        user = get_user_by_header_request(self)
        user_id = user.id

        response = services.user_get_general_state(user_id)

        return HttpResponse(json.dumps(response), status=200)
    else:
        return HttpResponse('', status=405)


@decorator_from_middleware(MobileMiddleware)
def user_change_language(self):
    logger.info('Handling /user/language.')
    if self.method == 'POST':
        user = get_user_by_header_request(self)
        data = json.loads(self.body)
        language = data.get('language', None)

        if language is None:
            return HttpResponse('You should provide language parameter: PT, EN or ES.', status=400)

        if not language == 'pt' and not language == 'en' and not language == 'es':
            return HttpResponse('Malformed syntax in language parameter.', status=400)

        user.language = language
        user.save()

        return HttpResponse(json.dumps({}), status=200)

    else:
        return HttpResponse('', status=405)


@decorator_from_middleware(MobileMiddleware)
def user_change_font_size(self):
    logger.info('Handling /user/font.')
    if self.method == 'POST':
        user = get_user_by_header_request(self)
        data = json.loads(self.body)
        font_size = data.get('font_size', None)

        if font_size is None:
            return HttpResponse('You should provide font_size parameter: S, M or L.', status=400)

        if not font_size == 'S' and not font_size == 'M' and not font_size == 'L':
            return HttpResponse('Malformed syntax in font_size parameter.', status=400)

        user.font_size = font_size
        user.save()
        return HttpResponse(json.dumps({}), status=200)

    else:
        return HttpResponse('', status=405)


@decorator_from_middleware(MobileMiddleware)
def list_category_magazines(self):
    if self.method == 'GET':
        try:
            response = dict()

            response['solr_version'] = services.solr_repository_version()

            order_en = list(Category.objects.all().order_by('category_name_en').values_list('id', flat=True))
            order_pt = list(Category.objects.all().order_by('category_name_pt').values_list('id', flat=True))
            order_es = list(Category.objects.all().order_by('category_name_es').values_list('id', flat=True))

            response['categories_order_en'] = order_en
            response['categories_order_pt'] = order_pt
            response['categories_order_es'] = order_es

            categories = Category.objects.all()
            response['categories'] = {}

            for category in categories:
                response['categories'][category.id] = category.to_dict()
                magazines = list(
                    Magazine.objects.filter(categories=category).order_by('magazine_name').values_list('id', flat=True))
                response['categories'][category.id]['magazines'] = magazines

            magazines = Magazine.objects.all()
            response['magazines'] = {}
            for magazine in magazines:
                response['magazines'][magazine.id] = magazine.to_dict()

            response['magazines_order'] = list(
                Magazine.objects.all().order_by('magazine_name').values_list('id', flat=True))

            return HttpResponse(json.dumps(response), status=200)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    else:
        return HttpResponse('', status=405)


@decorator_from_middleware(MobileMiddleware)
def solr_version(self):
    if self.method == 'GET':
        try:
            return HttpResponse(json.dumps(services.solr_repository_version()), status=200)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
    else:
        return HttpResponse('', status=405)
# endregion


# region BACKOFFICE

# region LOGIN/SIGNIN
def bo_administrator_login(self):
    try:
        logger.info('Handling /backoffice/users/login.')
        if self.method == 'POST':
            stream = BytesIO(self.body)
            data = JSONParser().parse(stream)

            credentials = dict()

            credentials['email'] = data.get('email', None)
            credentials['password'] = data['password'].encode('utf-8')

            try:
                administrator = Administrator.objects.get(email=credentials['email'], password__isnull=False, active=True)
            except Administrator.DoesNotExist:
                logger.warning('Login with administrator ({email}) failed. Administrator not found.'.format(email=credentials['email']))
                raise CustomException(CustomErrorMessages.USER_NOT_FOUND)

            if not bcrypt.hashpw(credentials['password'], administrator.password.encode('utf-8')) == administrator.password.encode('utf-8'):
                logger.warning('Login with administrator ({email}) failed. Password doesn\'t match.'.format(email=credentials['email']))
                raise CustomException(CustomErrorMessages.INVALID_CREDENTIALS)

            response = dict()
            response['token'] = jwt_util.jwt_auth_generate_token(credentials)

            return HttpResponse(json.dumps(response), status=200)
        else:
            return HttpResponse(status=405)
    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


@decorator_from_middleware(BackofficeAuthMiddleware)
def bo_administrator_me(self):
    try:
        logger.info('Handling /backoffice/users/me.')
        if self.method == 'GET':
            token = self.META.get('HTTP_AUTHORIZATION', None)
            user = jwt_util.jwt_auth_get_user(token)

            return HttpResponse(json.dumps(AdministratorSerializer(user).data), status=200)
        else:
            return HttpResponse(status=405)
    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


@decorator_from_middleware(BackofficeAuthMiddleware)
def bo_administrator_change_password(self):
    try:
        logger.info('Handling /backoffice/users/change-password.')
        if self.method == 'POST':
            stream = BytesIO(self.body)
            data = JSONParser().parse(stream)

            if not 'current_password' in data or not 'new_password' in data:
                return HttpResponse(status=401)

            current_password = data['current_password'].encode('utf-8')
            new_password = data['new_password'].encode('utf-8')

            token = self.META.get('HTTP_AUTHORIZATION', None)
            user = jwt_util.jwt_auth_get_user(token)

            if not bcrypt.hashpw(current_password, user.password.encode('utf-8')) == user.password.encode('utf-8'):
                raise CustomErrorMessages(CustomErrorMessages.INVALID_CREDENTIALS)

            hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt())

            user.password = hashed_password
            user.save()

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=405)

    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


def bo_administrator_set_password(self):
    try:
        logger.info('Handling /backoffice/users/set-password.')
        if self.method == 'POST':
            stream = BytesIO(self.body)
            data = JSONParser().parse(stream)

            if not 'token' in data or not 'new_password' in data:
                return HttpResponse(status=401)

            token = data.get('token', None)
            new_password = data['new_password'].encode('utf-8')

            user = jwt_util.jwt_auth_get_user(token)

            hashed_password = bcrypt.hashpw(new_password, bcrypt.gensalt())

            user.password = hashed_password
            user.save()

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=405)

    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


def bo_administrator_recover_password(self):
    try:
        logger.info('Handling /backoffice/users/recover-password.')
        if self.method == 'POST':
            stream = BytesIO(self.body)
            data = JSONParser().parse(stream)

            if 'email' not in data:
                return HttpResponse(status=401)

            user_credentials = dict()

            user_credentials['email'] = data.get('email', None)

            if not Administrator.objects.filter(email=user_credentials['email']).exists():
                raise CustomException(CustomErrorMessages.USER_NOT_FOUND)

            token = jwt_util.jwt_recovery_generate_token(user_credentials)
            thread.start_new_thread(email_sender.send_password_recovery_email, (user_credentials['email'], token))
            logger.info('Recovery token: ' + str(token))

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=405)

    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


def bo_administrator_validate_recovery_token(self):
    try:
        logger.info('Handling /backoffice/users/validate-recovery-token.')
        if self.method == 'POST':
            stream = BytesIO(self.body)
            data = JSONParser().parse(stream)

            if 'token' not in data:
                return HttpResponse(status=401)

            user = jwt_util.jwt_recovery_get_user(data['token'])

            return HttpResponse(json.dumps(AdministratorSerializer(user).data), status=200)
        else:
            return HttpResponse(status=405)

    except CustomException as e:
        return HttpResponse(e.message, status=450)
    except:
        logger.critical(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)

# endregion


# region ADMINISTRATOR CRUD
@decorator_from_middleware(BackofficeAuthMiddleware)
def bo_administrator_save(self):
    try:
        logger.info('Handling /backoffice/users/save.')
        if self.method == 'POST':
            token = self.META.get('HTTP_AUTHORIZATION', None)
            user = jwt_util.jwt_auth_get_user(token)

            stream = BytesIO(self.body)
            data = JSONParser().parse(stream)

            if user.profile == 0:
                removed_magazines = Magazine.objects.all().values_list('id', flat=True)
            else:
                removed_magazines = user.magazines.all().values_list('id', flat=True)

            new_user = False

            try:
                admin = Administrator.objects.get(email=data.get('email', None))
                admin.magazines = admin.magazines.exclude(id__in=removed_magazines)
            except Administrator.DoesNotExist:
                admin = None
                new_user = True

            serializer = AdministratorSerializer(admin, data=data)

            if not serializer.is_valid():
                return HttpResponse(status=401)

            if serializer.validated_data.get('id', None) is None and admin is not None:
                raise CustomException(CustomErrorMessages.USER_ALREADY_EXISTS)

            magazines = serializer.validated_data.get('magazines', [])
            magazines = [val['id'] for val in magazines]

            if not (user.profile == 0 or (set(magazines).issubset(set(removed_magazines)) and serializer.validated_data.get('profile', None) == 2)):
                raise CustomException(CustomErrorMessages.NOT_ALLOWED_FOR_PROFILE)

            admin = serializer.save()

            if new_user:
                user_credentials = dict()
                user_credentials['email'] = admin.email

                token = jwt_util.jwt_recovery_generate_token(user_credentials)

                thread.start_new_thread(email_sender.send_welcome_email, (admin.email, token))

            if not user.profile == 0:
                magazines = admin.magazines.filter(id__in=user.magazines.all().values_list('id', flat=True))
                admin = AdministratorSerializer(admin).data
                admin['magazines'] = MagazineSerializer(magazines, many=True).data

            return HttpResponse(json.dumps(AdministratorSerializer(admin).data), status=200)
        else:
            return HttpResponse(status=405)
    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


@decorator_from_middleware(BackofficeAuthMiddleware)
def bo_administrator_list(self):
    try:
        logger.info('Handling /backoffice/users/list.')
        if self.method == 'GET':
            token = self.META.get('HTTP_AUTHORIZATION', None)
            user = jwt_util.jwt_auth_get_user(token)

            # magazines_id = user.magazines.all().values_list('id', flat=True)

            if user.profile == 0:
                queryset = Administrator.objects.filter(active=True).order_by('-create_time')
                administrators = AdministratorSerializer(queryset, many = True).data
            elif user.profile == 1:
                queryset = Administrator.objects.filter(active=True, profile=2).order_by('-create_time')
                administrators = []

                for result in queryset:
                    admin = AdministratorSerializer(result).data

                    logger.info(type(admin))
                    logger.info(admin)

                    admin['magazines'] = MagazineSerializer(result.magazines.filter(id__in=user.magazines.all().values_list('id', flat=True)), many=True).data

                    logger.info(admin)

                    administrators.append(admin)
            else:
                administrators = []

            return HttpResponse(json.dumps(administrators), status=200)
        else:
            return HttpResponse(status=405)

    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


@decorator_from_middleware(BackofficeAuthMiddleware)
def bo_administrator_delete(self, pk):
    try:
        logger.info('Handling /backoffice/users/delete')

        if self.method == 'DELETE':
            try:
                administrator = Administrator.objects.get(id=pk)

                administrator.active = False
                administrator.save()
            except Administrator.DoesNotExist:
                raise CustomException(CustomErrorMessages.USER_NOT_FOUND)

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=405)
    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)
# endregion


# region CATEGORIES
@decorator_from_middleware(BackofficeAuthMiddleware)
def bo_category_list(self):
    try:
        logger.info('Handling /backoffice/category.svc/list.')

        if self.method == 'GET':
            categories = Category.objects.all()

            return HttpResponse(json.dumps(CategorySerializer(categories, many=True).data), status=200)
        else:
            return HttpResponse(status=405)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)
# endregion


# region MAGAZINES
@decorator_from_middleware(BackofficeAuthMiddleware)
def bo_magazine_list(self):
    try:
        logger.info('Handling /backoffice/magazine.svc/list.')
        if self.method == 'GET':
            try:
                token = self.META.get('HTTP_AUTHORIZATION', None)

                user = jwt_util.jwt_auth_get_user(token)

                if user.profile == 0:
                    magazines = Magazine.objects.all()
                else:
                    magazines = Magazine.objects.filter(administrator=user)

                return HttpResponse(json.dumps(MagazineSerializer(magazines, many=True).data), status=200)
            except Administrator.DoesNotExist:
                raise CustomException(CustomErrorMessages.USER_NOT_FOUND)

        else:
            return HttpResponse(status=405)
    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)
# endregion


@decorator_from_middleware(BackofficeAuthMiddleware)
@transaction.atomic
def bo_cover_save(self):
    try:
        with transaction.atomic():
            logger.info('Handling /backoffice/articles/upload-cover.')
            if self.method == 'POST':
                token = self.META.get('HTTP_AUTHORIZATION', None)
                article_id = self.POST.get('article_id', None)
                image = self.FILES['file']

                article = solr_service.get_article(article_id)
                user = jwt_util.jwt_auth_get_user(token)

                if not validator.user_can_perform_cover_management(user.id, article):
                    raise CustomException(CustomErrorMessages.NOT_ALLOWED_FOR_PROFILE)

                try:
                    cover_article = CoverArticle.objects.get(article_id=article_id)
                    cover_article.image.delete()
                except CoverArticle.DoesNotExist:
                    cover_article = CoverArticle(article_id=article_id)
                    cover_article.magazine = Magazine.objects.get(id=article['journal_id'])

                cover_article.administrator = user
                cover_article.save()

                cover_article.image.save(str(uuid.uuid4()) + '.png', image)

                cover_article.save()

                article['image_upload_date'] = cover_article.upload_time
                article['image_upload_path'] = cover_article.image
                article['image_uploader'] = user.name

                solr_service.add_article(article)

                return HttpResponse(json.dumps(CoverArticleSerializer(cover_article).data), status=200)
            else:
                return HttpResponse(status=405)
    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


@decorator_from_middleware(BackofficeAuthMiddleware)
def bo_cover_delete(self, article_id):
    try:
        logger.info('Handling /backoffice/articles/delete-cover/' + str(article_id))
        if self.method == 'DELETE':
            token = self.META.get('HTTP_AUTHORIZATION', None)

            article = solr_service.get_article(article_id)
            user = jwt_util.jwt_auth_get_user(token)

            if not validator.user_can_perform_cover_management(user.id, article):
                raise CustomException(CustomErrorMessages.NOT_ALLOWED_FOR_PROFILE)

            try:
                cover_article = CoverArticle.objects.get(article_id=article_id)

                cover_article.image.delete()
                cover_article.delete()

            except CoverArticle.DoesNotExist:
                pass

            article['image_upload_date'] = None
            article['image_upload_path'] = None
            article['image_uploader'] = None

            solr_service.add_article(article)

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=405)
    except CustomException as ce:
        return HttpResponse(ce.message, status=450)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)


def bo_cover_get(self, article_id):
    try:
        logger.info('Handling /backoffice/articles/get-cover')
        if self.method == 'GET':
            try:
                cover_article = CoverArticle.objects.get(article_id=article_id)

                return HttpResponse(cover_article.image, content_type='image/png', status=200)
            except CoverArticle.DoesNotExist:
                pass

            return HttpResponse(status=200)
        else:
            return HttpResponse(status=405)
    except:
        logger.error(traceback.format_exc())
        return HttpResponse(CustomErrorMessages.UNEXPECTED_ERROR, status=500)
# endregion
