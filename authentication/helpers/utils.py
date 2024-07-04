from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str


def authenticate_uuid_token(uidb64, token):
    """
        This function is used to authenticate a user using a token and a uid.
        It returns the user and uid if the token is valid, otherwise it returns None.
    """

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        return user, uid

    return None