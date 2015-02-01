# coding=utf-8
from base import BaseTestCase


class BasicErrorPageTest(BaseTestCase):
    def test_404_is_returned_when_nonexistent_page_is_requested(self):
        # Bob tries to fetch a page, that certainly does not exist.
        response = self.testapp.get('/i_do_not_exist', expect_errors=True)

        # He receives a 404 and a brief error text.
        self.assertTitleEqual(response, 'MyWiki *** Page not found')
        self.assertEqual(response.status_int, 404)
        self.assertEqual(
            response.pyquery('#error-message').text(), 'Page not found')

        # Top panel is present on the page too.
        self.assertEqual(len(response.pyquery('#top-panel')), 1)

        # There is also a link to the homepage.
        self.assertHasLinkToHomepage(response)

    def logging_out_at_error_page_redirects_to_homepage(self):
        # Bob tries to fetch a page, that certainly does not exist. He receives
        # a 404.
        error_page = self.testapp.get('/i_do_not_exist', expect_errors=True)

        # He clicks a "Sign Out" link and is redirected to homepage as a result.
        response = error_page.click(linkid='logout-link').follow()
        self.assertTitleEqual(response, u'MyWiki — Welcome to MyWiki!')