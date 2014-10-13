from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe


from invitation import (utils, models)
from invitation.models import InvitationKey


reg_backend_str = getattr(settings, 'INVITE_REGISTRATION_BACKEND',
                       'allauth.account.auth_backends.AuthenticationBackend')
DefaultBackend = utils.str_to_class(reg_backend_str)

# TODO: delete when sure don't need
# if getattr(settings, 'INVITATION_USE_ALLAUTH', False):
#     from allauth.account.auth_backends import AuthenticationBackend
# else:
#     from registration.backends.default import DefaultBackend


class BaseRegistrationBackend():
    """
    Base class for registration backends to be used with invitations.  To
    create a custom backend, inherit from this class and implement the methods
    """

    template = None
    backend = None

    def get_backend(self):
        return self.backend

    def get_registration_form(self):
        raise NotImplementedError("Create a subclass and implement method")

    def get_registration_template(self):
        return self.template

    def get_registration_view(self):
        raise NotImplementedError("Create a subclass and implement method")


class RegistrationBackend(BaseRegistrationBackend):

    template = 'registration/registration_form.html'
    backend = 'registration.backends.default.DefaultBackend'

    def get_registration_form(self):
        from registration.forms import RegistrationForm
        return RegistrationForm

    def get_registration_view(self):
        from registration.views import register
        return register


class AllAuthRegistrationBackend(RegistrationBackend):

    template = 'account/signup.html'
    backend = 'allauth.account.auth_backends.AuthenticationBackend'

    def get_registration_form(self):
        from allauth.socialaccount.forms import SignupForm
        return SignupForm

    def get_registration_view(self):
        from allauth.account.views import signup as allauth_signup

        def register(request, backend, success_url, form_class, disallowed_url,
                     template_name, extra_context):
            return allauth_signup(request, template_name=template_name)
        return register


class InvitationMixin():

    def post_registration_redirect(self, request, user, *args, **kwargs):
        """
        Return the name of the URL to redirect to after successful
        user registration.

        """
        invitation_key = request.REQUEST.get('invitation_key')
        key = InvitationKey.objects.get_key(invitation_key)
        if key:
            key.mark_used(user)

            # delete it from the session too
            del request.session['invitation_key']

        return ('registration_complete', (), {})


class InvitationBackend(InvitationMixin, DefaultBackend):
    pass


class BaseDeliveryBackend():

    def __init__(self, data):
        self.data = data

    def get_recipient_dict(self):
        raise NotImplementedError("Create a subclass and implement method")

    def create_invitation(self, user):
        recipient_dict = self.get_recipient_dict()
        return InvitationKey.objects.create_invitation(user, recipient_dict)

    def send_invitation(self, context):
        c = {}
        c.update(context)
        c.update(self.get_extra_context())
        self._send_invitation(c)

    def _send_invitation(self, context):
        raise NotImplementedError("Create a subclass and implement method")

    def get_extra_context(self):
        raise NotImplementedError("Create a subclass and implement method")


class EmailDeliveryBackend(BaseDeliveryBackend):
    subject_template = 'invitation/invitation_email_subject.txt'
    html_template = 'invitation/invitation_email.html'
    text_template = 'invitation/invitation_email.txt'

    def get_recipient_dict(self):
        return {models.KEY_EMAIL: self.data.get('email')}

    def get_extra_context(self):
        return {'sender_note': self.data.get("sender_note", "")}

    def _send_invitation(self, context):
        subject = render_to_string(self.subject_template, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message_html = render_to_string(self.html_template, context)
        note = mark_safe(strip_tags(context.get('sender_note')))
        context.update({'sender_note': note})
        message = render_to_string(self.text_template, context)
        default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL',
                                     'set_DEFAULT_FROM_EMAIL@thissite.com')
        msg = EmailMultiAlternatives(subject, message,
                                     context.get('from_email',
                                                 default_from_email),
                                     [context.get('recipient_email')])
        msg.attach_alternative(message_html, "text/html")
        msg.send()


class NamedEmailDeliveryBackend(EmailDeliveryBackend):

    def get_recipient_dict(self):
        d = super(NamedEmailDeliveryBackend, self).get_recipient_dict()
        d.update({
            models.KEY_FNAME, self.data.get('first_name'),
            models.KEY_LNAME, self.data.get('last_name'),
        })
        return d
