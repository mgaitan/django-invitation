from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login


@receiver(pre_social_login, dispatch_uid="allauth.socialaccount.helper")
def pre_social_login_handler(sender, request, **kwargs):
    # todo: Should check if invitation key is in session and it is valid.
    # Straight return false.
    return False
