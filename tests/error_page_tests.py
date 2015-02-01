# coding=utf-8
from base import BaseTestCase


class NotFoundErrorPageTest(BaseTestCase):
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

    def test_404_page_offers_user_to_login_or_sign_up(self):
        # Bob tries to fetch a page, that certainly does not exist. He receives
        # a 404.
        error_page = self.testapp.get('/i_do_not_exist', expect_errors=True)

        # However, he sees, that page offers him to log in or sign up to create
        # the page he requested.
        auth_offer = error_page.pyquery('#auth-offer')
        self.assertTrue(bool(auth_offer))
        self.assertEqual(
            auth_offer.text(),
            'Sign in or sign up to create the page you requested.')

        # There are two links in the offer, that lead to corresponding pages.
        login_offer = auth_offer.find('#login-offer-link')
        signup_offer = auth_offer.find('#signup-offer-link')
        self.assertTrue(bool(login_offer))
        self.assertTrue(bool(signup_offer))
        self.assertEqual(login_offer.attr.href, '/login')
        self.assertEqual(signup_offer.attr.href, '/signup')