from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model
from invitation.models import InvitationUser


class Command(BaseCommand):
    help = "Sets invites_allocated to -1 to represent infinite invites."

    def handle(self, *args, **kwargs):
        for user in get_user_model().objects.all():
            invite_user, _ = InvitationUser.objects.get_or_create(user=user)
            invite_user.invites_allocated = -1
            invite_user.save()