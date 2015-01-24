# coding=utf-8
from base import BaseTestCase


class BasicViewPageTest(BaseTestCase):
    def test_404_is_returned_when_nonexistent_page_is_requested(self):
        # Bob tries to fetch a page, that certainly does not exist.
        response = self.testapp.get('/i_do_not_exist', expect_errors=True)

        # He receives a 404 and a brief error text.
        self.assertTitleEqual(response, u'MyWiki — Page not found')
        self.assertEqual(response.status_int, 404)
        self.assertEqual(
            response.pyquery('#error-message').text(), 'Page not found')

        # Top panel is present on the page too.
        self.assertEqual(len(response.pyquery('#top-panel')), 1)
