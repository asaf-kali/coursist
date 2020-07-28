import sentry_sdk
from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.signals import pre_social_login
from django.conf import settings
from django.dispatch import receiver
from django.shortcuts import redirect

from academic_helper.models import CoursistUser
from academic_helper.utils.logger import log, wrap


# Copied from
# https://stackoverflow.com/questions/24357907/django-allauth-facebook-redirects-to-signup-when-retrieved-email-matches-an-exis


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Overrides allauth.socialaccount.adapter.DefaultSocialAccountAdapter.pre_social_login to
    perform some actions right after successful login
    """

    def pre_social_login(self, request, sociallogin):
        try:
            log.info(f"Social login by: {sociallogin.email_addresses}")
        except Exception as e:
            sentry_sdk.capture_exception(e)


@receiver(pre_social_login)
def link_to_local_user(sender, request, sociallogin, **kwargs):
    """
    Login and redirect
    This is done in order to tackle the situation where user's email retrieved
    from one provider is different from already existing email in the database
    (e.g facebook and google both use same email-id). Specifically, this is done to
    tackle following issues:
    * https://github.com/pennersr/django-allauth/issues/215
    """
    email_address = sociallogin.account.extra_data["email"]
    try:
        existing = CoursistUser.objects.get(email=email_address)
        log.info(f"Email {wrap(email_address)} was found, associated with user {wrap(existing.id)}")
        perform_login(request, existing, email_verification="optional")
        raise ImmediateHttpResponse(redirect(settings.LOGIN_REDIRECT_URL.format(id=request.user.id)))
    except CoursistUser.DoesNotExist:
        log.info(f"Email {wrap(email_address)} was not found, creating a new user")
