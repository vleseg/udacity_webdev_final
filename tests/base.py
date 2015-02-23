import unittest
# Third-party imports
from google.appengine.ext import testbed
from webtest import TestApp, TestResponse


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        # This is import is here because another import inside starts using
        # datastore right away.
        from main import app
        self.testapp = TestApp(app)

    def tearDown(self):
        self.testbed.deactivate()

    def create_article(self, url, sign_up=True, **fields):
        if sign_up:
            self.sign_up()
        edit_page = self.testapp.get('/_edit' + url)
        new_page = self.fill_form(edit_page, **fields).submit().follow()

        return new_page

    def edit_article(self, url, **fields):
        edit_page = self.testapp.get('/_edit' + url)
        modified_page = self.fill_form(edit_page, **fields).submit().follow()

        return modified_page

    def fill_form(self, page, **fields):
        form = page.form
        for f in fields:
            form[f] = fields[f]
        return form

    def sign_up(self, **params):
        if not params:
            params = {
                'username': 'bob', 'password': 'test123', 'verify': 'test123'}

        signup_page = self.testapp.get('/signup')
        self.fill_form(signup_page, **params).submit()

    def assertHasFormError(self, page, error_text):
        errors = page.pyquery('.form-errors')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors.text(), error_text)

    def assertHasLink(self, container, selector, text=None, href=None):
        if isinstance(container, TestResponse):
            container = container.pyquery('body')

        link = container.find(selector)
        self.assertTrue(bool(link))
        if text is not None:
            self.assertEqual(link.text(), text)
        if href is not None:
            self.assertEqual(link.attr('href'), href)

    def assertHasLinkToHomepage(self, page):
        self.assertHasLink(page, '#homepage-link', text='Home', href='/')

    def assertTitleEqual(self, page, title_text):
        self.assertEqual(page.pyquery('title').text(), title_text)
