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
        signin_page = self.testapp.get('/login')

        # There's a section on page, that offers new users to sign up.
        sign_up_offer = signin_page.pyquery('.auth-alternative')
        self.assertEqual(sign_up_offer.text(), 'Not a user? Sign up!')

        # This section contains a link, that leads to the registration page.
        signin_page.click(linkid='auth-alternative-link')

    def test_vague_error_message_on_wrong_credentials(self):
        # Bob signs up using standard test credentials (bob/ test123) and
        # immediately logs out.
        self.sign_up()
        self.testapp.get('/logout')

        # Bob opens the login page.
        login_page = self.testapp.get('/login')

        # Bob tries to sign in using nonexistent username.
        form = self.fill_form(login_page, username='alice', password='test123')
        login_submit_response = form.submit()

        # Page refreshes.
        self.assertTitleEqual(login_submit_response, u'MyWiki — Login')

        # There's a vague error message, that does not give a clue, what's wrong
        # with input data.
        self.assertHasFormError(
            login_submit_response,
            'Something is wrong with your username or password')

    def test_vague_error_message_on_empty_username(self):
        # Bob signs up using standard test credentials (bob/ test123) and
        # immediately logs out.
        self.sign_up()
        self.testapp.get('/logout')

        # Bob opens the login page.
        login_page = self.testapp.get('/login')

        # Bob tries to sign in without username.
        form = self.fill_form(login_page, username='', password='test123')
        login_submit_response = form.submit()

        # Page refreshes.
        self.assertTitleEqual(login_submit_response, u'MyWiki — Login')

        # There's a vague error message, that does not give a clue, what's wrong
        # with input data.
        self.assertHasFormError(
            login_submit_response,
            'Something is wrong with your username or password')

    def test_vague_error_message_on_empty_password(self):
        # Bob signs up using standard test credentials (bob/ test123) and
        # immediately logs out.
        self.sign_up()
        self.testapp.get('/logout')

        # Bob opens the login page.
        login_page = self.testapp.get('/login')

        # Bob tries to sign in without password.
        form = self.fill_form(login_page, username='bob', password='')
        login_submit_response = form.submit()

        # Page refreshes.
        self.assertTitleEqual(login_submit_response, u'MyWiki — Login')

        # There's a vague error message, that does not give a clue, what's wrong
        # with input data.
        self.assertHasFormError(
            login_submit_response,
            'Something is wrong with your username or password')


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