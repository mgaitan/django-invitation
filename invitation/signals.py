from django.dispatch import receiver, Signal
from allauth.socialaccount.signals import pre_social_login


invite_invited = Signal(providing_args=["invite_key"])
invite_accepted = Signal(providing_args=["registered_user", "invite_key"])


@receiver(pre_social_login, dispatch_uid="allauth.socialaccount.helper")
def pre_social_login_handler(sender, request,  **kwargs):
    # todo: Should check if invitation key is in session and it is valid.
    # Straight return false.
    return False
