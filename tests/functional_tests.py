# coding=utf-8
import unittest
# Third-party imports
from google.appengine.ext import testbed
import webtest


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        # This is import is here because another import inside starts using
        # datastore right away.
        from main import app
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.testbed.deactivate()

    def fill_form(self, page, **fields):
        form = page.form
        for f in fields:
            form[f] = fields[f]
        return form

    def assertTitleEqual(self, page, title_text):
        self.assertEqual(page.pyquery('title').text(), title_text)


class CreateNewUserTest(BaseTestCase):
    def test_can_create_a_new_user(self):
        # Bob types in signup page address and presses Enter. Browser
        # successfully delivers him a signup page.
        signup_page = self.testapp.get('/signup')
        self.assertEqual(signup_page.status_int, 200)

        # Page title says: "MyWiki -- Sign Up". There's also a heading and a
        # form. Heading is as follows: "Create new user account".
        self.assertTitleEqual(signup_page, u'MyWiki — Sign Up')
        heading = signup_page.pyquery('h1')
        self.assertEqual(heading.text(), 'Create new user account')
        self.assertEqual(len(signup_page.forms), 1)

        # Bob enters his name (bob) into "Username" field and uses "test123" as
        # password.
        form = self.fill_form(
            signup_page, username='bob', password='test123', verify='test123')

        # He does not specify email address, since it's optional. There's a
        # submit button below the form. It has a label: "Create".
        submit_button = signup_page.pyquery('input[type=submit]')
        self.assertEqual(submit_button.attr('value'), 'Create')

        # Bob submits the form. Browser redirects Bob to the home page. He can
        # tell that by looking at page title, it says: "MyWiki -- Welcome!"
        signup_submit_response = form.submit().follow()
        self.assertTitleEqual(signup_submit_response, u'MyWiki — Welcome!')

        # He can also see his name (bob) in the top area of the page.
        username = signup_submit_response.pyquery('#username').text()
        self.assertEqual(username, 'bob')


class UsernameValidationTest(BaseTestCase):
    def assertHasFormError(self, page, error_text):
        errors = page.pyquery('.form-errors')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors.text(), error_text)

    def test_can_not_create_user_with_empty_username(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')

        # Bob omits the "Usename" field, fills in "test123" in both "Password"
        # and "Verify password" fields.
        form = self.fill_form(signup_page, password='test123', verify='test123')

        # Bob submits the form.
        signup_submit_response = form.submit()

        # Signup page refreshes.
        self.assertTitleEqual(signup_submit_response, u'MyWiki — Sign Up')

        # Bob can see error message, complaining about absent username.
        self.assertHasFormError(signup_submit_response,
                                'You must specify username!')

        # "Password" and "Verify password" fields are empty.
        form = signup_submit_response.form
        self.assertEqual(form['password'].value, '')
        self.assertEqual(form['verify'].value, '')

    def test_username_should_not_be_overly_short(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')

        # Bob enters first two letters of his name into "Username" field and
        # uses "test123" as password.
        form = self.fill_form(
            signup_page, username='bo', password='test123', verify='test123')

        # He submits the form.
        signup_submit_response = form.submit()

        # Page refreshes.
        self.assertTitleEqual(signup_submit_response, u'MyWiki — Sign Up')

        # Bob can see error message, complaining about username length.
        self.assertHasFormError(
            signup_submit_response,
            'Username is too short! Must be 3 to 20 characters long')

        # Entered username is still available in "Username" field.
        form = signup_submit_response.form
        self.assertEqual(form['username'].value, 'bo')

    def test_username_should_not_be_overly_long(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')

        # Bob enters uses "bobkowalskifrommontaukonlongisland" as his username
        # and 'test123' as a password.
        form = self.fill_form(
            signup_page, username='bobkowalskifrommontaukonlongisland',
            password='test123', verify='test123')

        # He submits the form.
        signup_submit_response = form.submit()

        # Page refreshes.
        self.assertTitleEqual(signup_submit_response, u'MyWiki — Sign Up')

        # Bob can see error message, complaining about username length.
        self.assertHasFormError(
            signup_submit_response,
            'Username is too long! Must be 3 to 20 characters long')

        # Entered username is still available in "Username" field.
        form = signup_submit_response.form
        self.assertEqual(form['username'].value,
                         'bobkowalskifrommontaukonlongisland')

    def test_username_can_not_contain_invalid_characters(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')

        # Bob enters his name in Russian (боб) and uses 'test123' as password.
        form = self.fill_form(
            signup_page, username=u'боб', password='test123', verify='test123')

        # He submits the form.
        signup_submit_response = form.submit()

        # Page refreshes.
        self.assertTitleEqual(signup_submit_response, u'MyWiki — Sign Up')

        # Bob can see error message, complaining about invalid characters in
        # username.
        self.assertHasFormError(
            signup_submit_response,
            'Invalid username! May contain only latin letters, digits, '
            'dash and underscore')

        # Entered username is still available in "Username" field.
        form = signup_submit_response.form
        self.assertEqual(form['username'].value, u'боб')

    def test_can_not_create_user_if_username_already_exists(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')
        
        # Bob enters his name (bob) in "Username" field and uses 'test123' as a
        # password.
        form = self.fill_form(
            signup_page, username='bob', password='test123', verify='test123')
        
        # Bob submits the form.
        form.submit().follow()
        
        # He logs out.
        self.testapp.get('/logout')
        
        # Bob visits signup page once again.
        signup_page = self.testapp.get('/signup')
        
        # He enters the same user credentials as before.
        form = self.fill_form(
            signup_page, username='bob', password='test123', verify='test123')
        
        # Bob submits the form.
        signup_submit_response = form.submit()

        # Page refreshes.
        self.assertTitleEqual(signup_submit_response, u'MyWiki — Sign Up')

        # Bob sees an error message, complaining about user already existing.
        self.assertHasFormError(
            signup_submit_response, 'User "bob" already exists!')

        # Username he provided is still in the "Username" field.
        form = signup_submit_response.form
        self.assertEqual(form['username'].value, 'bob')


class PasswordValidationTest(BaseTestCase):
    def test_can_not_create_user_without_password(self):
        # Bob goes to signup page.

        # Bob enters his name (bob) into "Username" field.

        # He omits "Password" and "Verify password" fields and submits the form.

        # Signup page refreshes and he can see error message next to "Password"
        # field.

        # "Username" field still has his name (bob) in it.
        pass

    def test_password_can_not_be_overly_long(self):
        pass

    def test_password_can_not_be_overly_short(self):
        pass

    def test_has_to_verify_password_to_create_a_user(self):
        # Bob goes to signup page.

        # Bob enters his name (bob) into "Username" field.

        # He enters "test123" into "Password" field.

        # He mistypes confirmation password, entering "test124" into "Verify
        # password" field.

        # Bob submits the form.

        # Signup page refreshes and he can see error message next to "Verify
        # password" field.

        # Both "Password" and "Verify password" fields are empty. "Username"
        # field still has his name in it.
        pass


class EmailValidationTest(BaseTestCase):
    def test_email_if_entered_has_to_be_valid(self):
        # Bob goes to signup page.

        # Bob enters his name (bob) into "Username" field.

        # He enters "test123" into both "Password" and "Verify" fields.

        # He enters "bob@examplecom" into "Email" field, accidentally missing
        # a dot before "com".

        # Bob submits the form.

        # Signup page refreshes and he can see error message, complaining about
        # incorrect email address.

        # Both "Password" and "Verify password" fields are empty. "Username" and
        # "Email" fields still have corresponding values in them.
        pass