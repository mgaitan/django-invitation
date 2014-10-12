import sys

from django.core.management.base import BaseCommand

from invitation.models import InvitationUser


class Command(BaseCommand):
    help = "Makes sure all users have a certain number of invites."

    def handle(self, *args, **kwargs):
        if len(args) == 0:
            sys.exit("You must supply the number of invites as an argument.")

        try:
            num_of_invites = int(args[0])
        except ValueError:
            sys.exit("The argument for number of invites must be an integer.")

        InvitationUser.topoff(num_of_invites)