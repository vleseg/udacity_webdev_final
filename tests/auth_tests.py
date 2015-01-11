# coding=utf-8
from base import BaseTestCase


class LoginTest(BaseTestCase):
    def test_can_login_as_existing_user(self):
        # Bob creates a new user using signup page. He uses "bob" as username
        # and "test123" as password.
        signup_page = self.testapp.get('/signup')
        self.fill_form(signup_page, username='bob', password='test123',
                       verify='test123').submit()

        # He logs out.
        self.testapp.get('/logout')

        # Bob types in login page address and presses Enter. Browser
        # successfully delivers him a login page.
        login_page = self.testapp.get('/login')
        self.assertEqual(login_page.status_int, 200)

        # Page's title says "MyWiki — Login"; heading on the page says "Log in
        # to MyWiki"; there's also a login form.
        self.assertTitleEqual(login_page, u'MyWiki — Login')
        self.assertEqual(login_page.pyquery('h1').text(), 'Sign into MyWiki')
        self.assertEqual(len(login_page.forms), 1)