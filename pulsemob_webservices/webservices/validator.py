from models import Administrator
from custom_exception import CustomErrorMessages, CustomException
import logging

logger = logging.getLogger(__name__)


def user_can_perform_cover_management(user_id, article):
    try:
        user = Administrator.objects.get(id=user_id)
    except Administrator.DoesNotExist:
        logger.warning('Error validating cover management operation. Administrator ({id}) not found.'.format(id=user_id))
        raise CustomException(CustomErrorMessages.USER_NOT_FOUND)

    if user.profile == 0:
        return True

    magazine_id = article.get('journal_id', None)

    if Administrator.objects.filter(magazines=magazine_id, id=user_id).exists():
        return True

    logger.warning('Error validating cover management operation. Administrator ({id}) is not related to magazine ({magazine_id})'.format(id=user_id, magazine_id=magazine_id))
    return False


def user_can_perform_user_management(logged_user, updated_user=None):
    if logged_user.profile == 0:
        return True
    elif logged_user.profile == 2:
        return False
    else:
        return updated_user.profile == 2
