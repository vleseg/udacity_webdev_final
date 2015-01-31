# coding=utf-8
# Project-specific imports
from base import BaseTestCase


class CreateNewUserTest(BaseTestCase):
    def test_can_create_a_new_user(self):
        # Bob types in signup page address and presses Enter. Browser
        # successfully delivers him a signup page.
        signup_page = self.testapp.get('/signup')
        self.assertEqual(signup_page.status_int, 200)

        # Page title says: "MyWiki -- Sign Up". There's also a head and a
        # form. Head is as follows: "Create new user account".
        self.assertTitleEqual(signup_page, 'MyWiki *** Sign Up')
        head = signup_page.pyquery('h1')
        self.assertEqual(head.text(), 'Create new user account')
        self.assertEqual(len(signup_page.forms), 1)

        # Bob enters his name (bob) into "Username" field and uses "test123" as
        # password.
        form = self.fill_form(
            signup_page, username='bob', password='test123', verify='test123')

        # Bob submits the form. Browser redirects Bob to the home page. He can
        # tell that by looking at page title, it says: "MyWiki -- Welcome!"
        signup_submit_response = form.submit().follow()
        self.assertTitleEqual(
            signup_submit_response, u'MyWiki — Welcome to MyWiki!')

        # He can also see his name (bob) in the top area of the page.
        username = signup_submit_response.pyquery('#username').text()
        self.assertEqual(username, 'bob')

    def test_signup_page_offers_to_sign_in(self):
        # Bob opens the signup page.
        signup_page = self.testapp.get('/signup')

        # There's a section on page, that offers existing users to sign in.
        sign_in_offer = signup_page.pyquery('.auth-alternative')
        self.assertEqual(sign_in_offer.text(), 'Already a user? Sign in!')

        # There is a link, that leads to the login page.
        response = signup_page.click(linkid='auth-alternative')
        self.assertTitleEqual(response, 'MyWiki *** Login')


class UsernameValidationTest(BaseTestCase):
    def test_can_not_create_user_with_empty_username(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')

        # Bob omits the "Usename" field, fills in "test123" in both "Password"
        # and "Verify password" fields.
        form = self.fill_form(signup_page, password='test123', verify='test123')

        # Bob submits the form.
        signup_submit_response = form.submit()

        # Signup page refreshes.
        self.assertTitleEqual(signup_submit_response, 'MyWiki *** Sign Up')

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
        self.assertTitleEqual(signup_submit_response, 'MyWiki *** Sign Up')

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
        self.assertTitleEqual(signup_submit_response, 'MyWiki *** Sign Up')

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
        self.assertTitleEqual(signup_submit_response, 'MyWiki *** Sign Up')

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
        self.assertTitleEqual(signup_submit_response, 'MyWiki *** Sign Up')

        # Bob sees an error message, complaining about user already existing.
        self.assertHasFormError(
            signup_submit_response, 'User "bob" already exists!')

        # Username he provided is still in the "Username" field.
        form = signup_submit_response.form
        self.assertEqual(form['username'].value, 'bob')


class PasswordValidationTest(BaseTestCase):
    def test_can_not_create_user_without_password(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')

        # Bob enters his name (bob) into "Username" field.
        form = self.fill_form(signup_page, username='bob')

        # He omits "Password" and "Verify password" fields and submits the form.
        signup_submit_response = form.submit()

        # Signup page refreshes.
        self.assertTitleEqual(signup_submit_response, 'MyWiki *** Sign Up')
        
        # Bob can see error message next to "Password" field.
        self.assertHasFormError(
            signup_submit_response, 'You must specify password!')

        # "Username" field still has his name (bob) in it.
        form = signup_submit_response.form
        self.assertEqual(form['username'].value, 'bob')

    def test_password_can_not_be_overly_short(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')

        # Bob enters his name (bob) into "Username" field and uses 'te' as a
        # password.
        form = self.fill_form(
            signup_page, username='bob', password='te', verify='te')

        # He submits the form.
        signup_submit_response = form.submit()

        # Page refreshes.
        self.assertTitleEqual(signup_submit_response, 'MyWiki *** Sign Up')

        # Bob can see error message, complaining about password length
        self.assertHasFormError(
            signup_submit_response,
            'Password is too short! Must be 3 to 20 characters long')

        # Entered username is still available in "Username" field.
        form = signup_submit_response.form
        self.assertEqual(form['username'].value, 'bob')

        # Entered passwords are no longer there.
        self.assertEqual(form['password'].value, '')
        self.assertEqual(form['verify'].value, '')

    def test_password_can_not_be_overly_long(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')

        # Bob enters his name (bob) into "Username" field and uses
        # 'unsafepasswordexclusivelyfortestingpurposes' as a password.
        form = self.fill_form(
            signup_page, username='bob',
            password='unsafepasswordexclusivelyfortestingpurposes',
            verify='unsafepasswordexclusivelyfortestingpurposes')

        # He submits the form.
        signup_submit_response = form.submit()

        # Page refreshes.
        self.assertTitleEqual(signup_submit_response, 'MyWiki *** Sign Up')

        # Bob can see error message, complaining about password length
        self.assertHasFormError(
            signup_submit_response,
            'Password is too long! Must be 3 to 20 characters long')

        # Entered username is still available in "Username" field.
        form = signup_submit_response.form
        self.assertEqual(form['username'].value, 'bob')

        # Entered passwords are no longer there.
        self.assertEqual(form['password'].value, '')
        self.assertEqual(form['verify'].value, '')

    def test_has_to_verify_password_to_create_a_user(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')

        # Bob enters his name (bob) into "Username" field and uses "test123"
        # as password. He also mistypes, entering "test124" into "Verify
        # password" field.
        form = self.fill_form(
            signup_page, username='bob', password='test123', verify='test124')

        # Bob submits the form.
        signup_submit_response = form.submit()

        # Signup page refreshes.
        self.assertTitleEqual(signup_submit_response, 'MyWiki *** Sign Up')

        # Bob can see error message, complaining about passwords not matching.
        self.assertHasFormError(
            signup_submit_response, 'Passwords do not match!')

        # Both "Password" and "Verify password" fields are empty.
        form = signup_submit_response.form
        self.assertEqual(form['password'].value, '')
        self.assertEqual(form['verify'].value, '')

        # "Username" field still has his name in it.
        self.assertEqual(form['username'].value, 'bob')


class EmailValidationTest(BaseTestCase):
    def test_email_if_entered_has_to_be_valid(self):
        # Bob goes to signup page.
        signup_page = self.testapp.get('/signup')

        # Bob enters his name (bob) into "Username" field and uses 'test123' as
        # his password. He also enters "bob@examplecom" into "Email" field,
        # accidentally missing out a dot before "com".
        form = self.fill_form(
            signup_page, username='bob', password='test123', verify='test123',
            email='bob@examplecom')

        # Bob submits the form.
        signup_submit_response = form.submit()

        # Signup page refreshes.
        self.assertTitleEqual(signup_submit_response, 'MyWiki *** Sign Up')

        # Bob can see error message, complaining about invalid email address.
        self.assertHasFormError(
            signup_submit_response, 'Invalid email address!')

        # Both "Password" and "Verify password" fields are empty.
        form = signup_submit_response.form
        self.assertEqual(form['password'].value, '')
        self.assertEqual(form['verify'].value, '')

        # "Username" and "Email" field still have corresponding data in them.
        self.assertEqual(form['username'].value, 'bob')
        self.assertEqual(form['email'].value, 'bob@examplecom')
