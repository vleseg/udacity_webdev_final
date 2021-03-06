from random import randint
import unittest
# Third-party imports
from google.appengine.ext import testbed
from webtest import TestApp, TestResponse


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        # This import is here, because another import inside starts using
        # datastore right away.
        from main import app
        self.testapp = TestApp(app)
        # The following is done because importing Article from inside test
        # modules fails, when one tries to run a separate test (not the whole
        # project).
        from model import Article
        self.article_model = Article

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

    def fetch_version_ids(self, article_url, rev_sort=False):
        article = self.article_model.by_url(article_url)
        version_ids = [v.id for v in article.version_set]
        if rev_sort:
            return reversed(sorted(version_ids))
        return sorted(version_ids)

    def fill_form(self, page, **fields):
        form = page.form
        for f in fields:
            form[f] = fields[f]
        return form

    def get_fake_version_id(self, article_url, rand_start=0, rand_end=10):
        version_ids = self.fetch_version_ids(article_url)
        random_version_id = randint(rand_start, rand_end)

        while random_version_id in version_ids:
            random_version_id = randint(rand_start, rand_end)

        return random_version_id

    def sign_up(self, **params):
        if not params:
            params = {
                'username': 'bob', 'password': 'test123', 'verify': 'test123'}

        signup_page = self.testapp.get('/signup')
        self.fill_form(signup_page, **params).submit()

    # Shared assertions.
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
