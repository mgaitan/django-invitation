from invitation.models import InvitationKey


def remaining_invitations(request):
    """
    determines if the user has any invitations remaining.
    """
    if request.user.is_authenticated():
        objs = InvitationKey.objects
        remaining_invites = objs.remaining_invitations_for_user(request.user)
    else:
        remaining_invites = None
    return {'remaining_invitations': remaining_invites}
