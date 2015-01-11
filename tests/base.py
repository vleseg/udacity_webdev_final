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

    def assertHasFormError(self, page, error_text):
        errors = page.pyquery('.form-errors')
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors.text(), error_text)