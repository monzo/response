from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def response_login_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    """
    Re-implementation of Django's login_required decorator to extend with
    support for allowing anonymous viewing if `RESPONSE_LOGIN_REQUIRED` is True.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated or not settings.RESPONSE_LOGIN_REQUIRED,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
