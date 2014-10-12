from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import re


class BaseInvitationKeyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.delivery_backend = kwargs.pop('delivery', getattr(settings,
                               'INVITATION_DELIVERY_BACKEND', 'default'))

        super(BaseInvitationKeyForm, self).__init__(*args, **kwargs)


class DefaultInvitationKeyForm(BaseInvitationKeyForm):
    email = forms.EmailField()
    sender_note = forms.CharField(widget=forms.Textarea, required=False,
                                  label='Your Note')

    def __init__(self, *args, **kwargs):
        self.remaining_invitations = kwargs.pop('remaining_invitations', None)
        self.user = kwargs.pop('user', None)
        self.invitation_blacklist = getattr(settings, 'INVITATION_BLACKLIST', ())

        super(DefaultInvitationKeyForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(DefaultInvitationKeyForm, self).clean()

        if self.remaining_invitations <= 0:
            err = _("Sorry, you don't have any invitations left")
            raise forms.ValidationError(err)

        if 'email' in self.cleaned_data:
            if self.user.email == self.cleaned_data['email']:
                err = _("You can't send an invitation to yourself")
                self._errors['email'] = self.error_class([err])
                del cleaned_data['email']

        if 'email' in self.cleaned_data:
            for email_match in self.invitation_blacklist:
                if re.search(email_match, self.cleaned_data['email']) is not None:
                    err = _("Thanks, but there's no need to invite us!")
                    self._errors['email'] = self.error_class([err])
                    del cleaned_data['email']
                    break

        if 'sender_note' in self.cleaned_data:
            if not self.user.is_staff and len(cleaned_data['sender_note']) > 500:
                err = _("Your note must be less than 500 characters")
                self._errors['sender_note'] = self.error_class([err])


class NamedInvitationKeyForm(DefaultInvitationKeyForm):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)

    def clean(self):
        cleaned_data = super(NamedInvitationKeyForm, self).clean()

        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')

        if first_name and last_name and email:
            cleaned_data['recipient'] = (email, first_name, last_name)

        # Always return the cleaned data, whether you have changed it or
        # not.
        return cleaned_data
