from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.safestring import mark_safe
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from invitation import utils
 
reg_backend_class = utils.get_registration_backend_class()
reg_backend = reg_backend_class()
DefaultBackend = utils.str_to_class(reg_backend.get_backend()) 

#TODO: delete when sure don't need
# if getattr(settings, 'INVITATION_USE_ALLAUTH', False):
#     from allauth.account.auth_backends import AuthenticationBackend as DefaultBackend
# else:
#     from registration.backends.default import DefaultBackend

from invitation.models import InvitationKey

class BaseRegistrationBackend():
    """
    Base class for registration backends to be used with invitations.  To create
    a custom backend, inherit from this class and implement the methods
    """
        
    def get_backend(self):
        raise NotImplementedError( "Create a subclass and implement this method" )
    
    def get_registration_form(self):
        raise NotImplementedError( "Create a subclass and implement this method" )
    
    def get_registration_template(self):
        raise NotImplementedError( "Create a subclass and implement this method" )
    
    def get_registration_view(self):
        raise NotImplementedError( "Create a subclass and implement this method" )


class RegistrationBackend(BaseRegistrationBackend):
    def get_backend(self):
        return 'registration.backends.default.DefaultBackend'
    
    def get_registration_form(self):
        from registration.forms import RegistrationForm
        return RegistrationForm
    
    def get_registration_template(self):
        return 'registration/registration_form.html'
    
    def get_registration_view(self):
        from registration.views import register
        return register
    
    
class AllAuthRegistrationBackend(RegistrationBackend):
    def get_backend(self):
        return 'allauth.account.auth_backends.AuthenticationBackend'
    
    def get_registration_form(self):
        from allauth.socialaccount.forms import SignupForm
        return SignupForm
    
    def get_registration_template(self):
        return 'account/signup.html'
    
    def get_registration_view(self):
        from allauth.socialaccount.views import signup as allauth_signup
    
        def register(request, backend, success_url, form_class, disallowed_url, template_name, extra_context):
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
    
    def __init__(self, user, form):
        self.form = form
        self.user = user
        
    def deliver(self):
        recipient_dict = self.get_recipient_dict()
        invitation = self.create_invitation(self.user, recipient_dict)
        context = invitation.get_context(self.get_extra_context())
        self.send_invitation(context)
        
    def get_recipient_dict(self):
        raise NotImplementedError( "Create a subclass and implement this method" )
    
    def create_invitation(self, user, recipient_dict):
        return InvitationKey.objects.create_invitation(user, recipient_dict)
    
    def send_invitation(self, context):
        raise NotImplementedError( "Create a subclass and implement this method" )
    
    def get_extra_context(self):
        raise NotImplementedError( "Create a subclass and implement this method" )
    

class EmailDeliveryBackend(BaseDeliveryBackend):
    subject_template = 'invitation/invitation_email_subject.txt'
    html_template = 'invitation/invitation_email.html'
    text_template = 'invitation/invitation_email.txt'
    
    def get_recipient_dict(self):
        return {InvitationKey.KEY_EMAIL, self.form.cleaned_data.get('email')}
    
    def get_extra_context(self):
        return {'sender_note': self.form.cleaned_data.get("sender_note")}
    
    def send_invitation(self, context):
        subject = render_to_string(self.subject_template, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        message_html = render_to_string(self.html_template,context)
        context.update({'sender_note':mark_safe(strip_tags(context.get('sender_note')))})
        message = render_to_string(self.text_template,context)
        msg = EmailMultiAlternatives(subject, message, context.get('from_email', settings.DEFAULT_FOM_EMAIL), [context.get('recipient_email')])
        msg.attach_alternative(message_html, "text/html")
        msg.send()


class NamedEmailDeliveryBackend(EmailDeliveryBackend):
    
    def get_recipient_dict(self):
        d = super(NamedEmailDeliveryBackend, self).get_recipient_dict()
        d.update({
                InvitationKey.KEY_FNAME, self.form.cleaned_data.get('first_name'),
                InvitationKey.KEY_LNAME, self.form.cleaned_data.get('last_name'),
        })
        return d
