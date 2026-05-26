from django.conf import settings
from django.shortcuts import redirect

EXEMPT_PREFIXES = ('/login/', '/admin/', '/static/', '/media/')


class PasswordProtectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(EXEMPT_PREFIXES):
            if not request.session.get('site_authenticated'):
                return redirect(f'/login/?next={request.path}')
        return self.get_response(request)
