# coding=utf-8
import unittest
# Third-party imports
from google.appengine.ext import testbed
import webtest


class CreateNewUserTest(unittest.TestCase):
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

    def test_can_create_a_new_user(self):
        # Bob types in signup page address and presses Enter. Browser
        # successfully delivers him a signup page.
        signup_page = self.testapp.get('/signup')
        self.assertEqual(signup_page.status_int, 200)

        # Page title says: "MyWiki -- Sign Up". There's also a heading and a
        # form. Heading is as follows: "Create new user account".
        pq_page = signup_page.pyquery('html')
        title = pq_page.find('title')
        heading = pq_page.find('h1')
        self.assertEqual(title.text(), u'MyWiki — Sign Up')
        self.assertEqual(heading.text(), 'Create new user account')
        self.assertEqual(len(signup_page.forms), 1)

        # Bob enters his name (bob) into "Username" field.
        form = signup_page.form
        form['username'] = 'bob'

        # Bob uses "test123" as password in "Password" field and confirms it in
        # "Verify password" field.
        form['password'] = 'test123'
        form['verify'] = 'test123'

        # He does not specify email address, since it's optional. There's a
        # submit button below the form. It has a label: "Create".
        submit_button = pq_page.find('input[type=submit]')
        self.assertEqual(submit_button.attr('value'), 'Create')

        # Bob submits the form. Browser redirects Bob to the home page. He can
        # tell that by looking at page title, it says: "MyWiki -- Welcome!" He
        # can also see his name (bob) in the top area of the page.
        signup_submit_response = form.submit().follow()
        pq_page = signup_submit_response.pyquery('html')
        title = pq_page.find('title')
        username = pq_page.find('#username')
        self.assertEqual(title.text(), u'MyWiki — Welcome!')
        self.assertEqual(username.text(), 'bob')

    def test_can_not_create_user_with_empty_username(self):
        # Bob goes to signup page.

        # Bob omits the "Usename" field, fills in "test123" in both "Password"
        # and "Verify password" fields.

        # Bob clicks "Create" button.

        # Signup page refreshes and he can see error message next to "Username"
        # field. "Password" and "Verify password" fields are empty.
        pass

    def test_can_not_create_user_without_password(self):
        # Bob goes to signup page.

        # Bob enters his name (bob) into "Username" field.

        # He omits "Password" and "Verify password" fields and clicks "Create"
        # button.

        # Signup page refreshes and he can see error message next to "Password"
        # field.

        # "Username" field still has his name (bob) in it.
        pass

    def test_has_to_verify_password_to_create_a_user(self):
        # Bob goes to signup page.

        # Bob enters his name (bob) into "Username" field.

        # He enters "test123" into "Password" field.

        # He mistypes confirmation password, entering "test124" into "Verify
        # password" field.

        # Bob clicks "Create" button.

        # Signup page refreshes and he can see error message next to "Verify
        # password" field.

        # Both "Password" and "Verify password" fields are empty. "Username"
        # field still has his name in it.
        pass