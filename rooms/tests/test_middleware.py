from django.test import TestCase, Client
from django.urls import reverse


class PasswordMiddlewareTest(TestCase):
    def setUp(self):
        self.client = Client()

    def _authenticate(self):
        session = self.client.session
        session['site_authenticated'] = True
        session.save()

    def test_unauthenticated_redirected_to_login(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/?next=/', fetch_redirect_response=False)

    def test_authenticated_can_access_root(self):
        self._authenticate()
        response = self.client.get('/')
        self.assertNotEqual(response.status_code, 302)

    def test_login_page_accessible_without_auth(self):
        response = self.client.get('/login/')
        self.assertNotEqual(response.status_code, 302)

    def test_admin_accessible_without_auth(self):
        response = self.client.get('/admin/')
        # admin redirects to its own /admin/login/, not our /login/
        location = response.get('Location', '')
        self.assertNotEqual(location, '/login/?next=/admin/')

    def test_static_prefix_exempt(self):
        response = self.client.get('/static/nonexistent.css')
        # WhiteNoise returns 404, not our redirect
        self.assertNotEqual(response.get('Location', ''), '/login/?next=/static/nonexistent.css')

    def test_media_prefix_exempt(self):
        response = self.client.get('/media/rooms/photo.jpg')
        self.assertNotIn('/login/', response.get('Location', ''))
