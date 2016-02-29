from models import Administrator
from rest_framework.exceptions import AuthenticationFailed
from custom_exception import CustomException, CustomErrorMessages
import jwt
import logging
import datetime

logger = logging.getLogger(__name__)

SECRET = '25f3a557-f700-45c4-a119-04a7bef3e97d'

# region Datetime handler functions
epoch = datetime.datetime.fromtimestamp(0)


def jwt_unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0


def jwt_get_expiration_time(expiration_time_in_hours=2):
    return jwt_unix_time_millis(datetime.datetime.now() + datetime.timedelta(hours=expiration_time_in_hours))
# endregion


# region Auth token handler functions
def jwt_auth_generate_token(user_credentials):
    user_credentials['expires_in'] = jwt_get_expiration_time()

    return jwt.encode(user_credentials, SECRET, algorithm='HS256')


def jwt_auth_validate_token(token, raise_exception=False):
    if token is None:
        if raise_exception:
            raise CustomException(CustomErrorMessages.TOKEN_MISSING)
        return False


    try:
        decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        raise CustomException(CustomErrorMessages.TOKEN_INVALID)

    expiration_datetime = datetime.datetime.fromtimestamp(decoded['expires_in']/1000.0)
    if expiration_datetime < datetime.datetime.now():
        if raise_exception:
            raise CustomException(CustomErrorMessages.TOKEN_EXPIRED)

        return False

    return True


def jwt_auth_get_user(token):
    jwt_auth_validate_token(token, raise_exception=True)

    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    email = decoded['email']

    try:
        return Administrator.objects.get(email=email, active=True)
    except Administrator.DoesNotExist:
        raise CustomException(CustomErrorMessages.USER_NOT_FOUND)

# endregion


# region Recovery token handler functions
def jwt_recovery_generate_token(user_credentials):
    user_credentials['expires_in'] = jwt_get_expiration_time(2)

    return jwt.encode(user_credentials, SECRET, algorithm='HS256')


def jwt_recovery_validate_token(token, raise_exception=False):
    try:
        decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        raise CustomException(CustomErrorMessages.TOKEN_INVALID)

    expiration_datetime = datetime.datetime.fromtimestamp(decoded['expires_in']/1000.0)
    if expiration_datetime < datetime.datetime.now():
        if raise_exception:
            raise CustomException(CustomErrorMessages.TOKEN_EXPIRED)

        return False

    return True


def jwt_recovery_get_user(token):
    jwt_recovery_validate_token(token, raise_exception=True)

    decoded = jwt.decode(token, SECRET, algorithms=['HS256'])
    email = decoded['email']

    try:
        return Administrator.objects.get(email=email, active=True)
    except Administrator.DoesNotExist:
        raise CustomException(CustomErrorMessages.USER_NOT_FOUND)
# endregion