from django.contrib.sites.models import Site, RequestSite

def get_site(request=None):
    site = None
    root_url = 'http://localhost'
    if Site._meta.installed:
        site = Site.objects.get_current()
        root_url = 'http://%s' % site.domain
    else: 
        if request:
            site = RequestSite(request)
    return site, root_url