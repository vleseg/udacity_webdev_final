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

        # Bob enters his username and password into corresponding fields.
        form = self.fill_form(login_page, username='bob', password='test123')

        # Bob submits the form.
        login_submit_response = form.submit().follow()

        # Browser redirects Bob to the home page. He can # tell that by looking
        # at page title, it says: "MyWiki -- Welcome!"
        self.assertTitleEqual(
            login_submit_response, u'MyWiki — Welcome to MyWiki!')

        # He can also see his name (bob) in the top area of the page.
        username = login_submit_response.pyquery('#username').text()
        self.assertEqual(username, 'bob')

    def test_login_page_offers_to_sign_up(self):
        # Bob opens the login page.
        signup_page = self.testapp.get('/login')

        # There's a section on page, that offers new users to sign up.
        sign_up_offer = signup_page.pyquery('.auth-alternative')
        self.assertEqual(sign_up_offer.text(), 'Not a user? Sign up!')

        # This section links to signup page.
        link_to_signup_page = sign_up_offer.find('a')
        self.assertEqual(link_to_signup_page.attr('href'), '/signup')

    def test_login_form_does_not_give_a_clue_what_is_wrong_when_it_is(self):
        # Bob creates a new user using signup page. He uses "bob" as username
        # and "test123" as password.
        signup_page = self.testapp.get('/signup')
        self.fill_form(signup_page, username='bob', password='test123',
                       verify='test123').submit()

        # He logs out.
        self.testapp.get('/logout')

        # Bob opens the login page.
        login_page = self.testapp.get('/login')

        # Bob tries to sign in using nonexistent username.
        form = self.fill_form(login_page, username='alice', password='test123')
        login_submit_response = form.submit()

        # Page refreshes.
        self.assertTitleEqual(login_submit_response, u'MyWiki — Login')


class LogoutTest(BaseTestCase):
    def test_logs_out_flawlessly(self):
        # Bob creates a new user using signup page.
        signup_page = self.testapp.get('/signup')
        home_page = self.fill_form(
            signup_page, username='bob', password='test123',
            verify='test123').submit().follow()

        # Browser redirects him to homepage. He can see his username in upper
        # part of the page.
        top_panel = home_page.pyquery('#top-panel')
        self.assertIn('bob', top_panel.text())

        # Bob logs out.
        home_page = self.testapp.get('/logout').follow()

        # Browser redirects him to homepage.
        self.assertTitleEqual(home_page, u'MyWiki — Welcome to MyWiki!')

        # Now his name isn't displayed on page.
        top_panel = home_page.pyquery('#top-panel')
        self.assertNotIn('bob', top_panel.text())