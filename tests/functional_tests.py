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
        form = pq_page.find('form')
        self.assertEqual(title.text(), u'MyWiki — Welcome!')
        self.assertEqual(heading.text(), 'Create new user account')
        self.assertNotEqual(len(form), 0)

        # Bob enters his name (bob) into "Username" field.
        #
        # Bob uses "test123" as password in "Password" field and confirms it in
        # "Verify password" field.

        # He does not specify email address, since it's optional. Bob presses
        # "Create new user" button.

        # Browser redirects Bob to the home page. He can tell that by looking at
        # page title, it says: "MyWiki -- Welcome!" He can also see his name
        # (bob) in the top area of the page.
        pass

    def test_can_not_create_user_with_empty_username(self):
        # Bob goes to signup page.

        # Bob omits the "Usename" field, fills in "test123" in both "Password"
        # and "Verify password" fields.

        # Bob clicks "Create new user" button.

        # Signup page refreshes and he can see error message next to "Username"
        # field. "Password" and "Verify password" fields are empty.
        pass

    def test_can_not_create_user_without_password(self):
        # Bob goes to signup page.

        # Bob enters his name (bob) into "Username" field.

        # He omits "Password" and "Verify password" fields and clicks "Create
        # new user" button.

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

        # Bob clicks "Create new user button".

        # Signup page refreshes and he can see error message next to "Verify
        # password" field.

        # Both "Password" and "Verify password" fields are empty. "Username"
        # field still has his name in it.
        pass