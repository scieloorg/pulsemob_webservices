from models import Administrator
from custom_exception import CustomErrorMessages, CustomException
import logging

logger = logging.getLogger(__name__)


def user_can_perform_cover_management(user_id, article):
    try:
        user = Administrator.objects.get(id=user_id)
    except Administrator.DoesNotExist:
        logger.warning('Error validating ({email}) cover management operation. Administrator not found.'.format(id=user_id))
        raise CustomException(CustomErrorMessages.USER_NOT_FOUND)

    if user.profile == 0:
        return True

    magazine_id = article.get('journal_title_id', None)

    logger.info('journal_title_id: ' + str(magazine_id))
    logger.info('user_id: ' + str(user_id))

    if Administrator.objects.filter(magazines=magazine_id, id=user_id).exists():
        logger.info('user_can_perform_cover_management: True')
        return True

    logger.info('user_can_perform_cover_management: False')
    return False


def user_can_perform_user_management(logged_user, updated_user=None):
    if logged_user.profile == 0:
        return True
    elif logged_user.profile == 2:
        return False
    else:
        return updated_user.profile == 2
