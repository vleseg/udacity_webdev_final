# coding=utf-8
from base import BaseTestCase


class NotFoundErrorPageTest(BaseTestCase):
    def test_404_is_returned_when_nonexistent_page_is_requested(self):
        # Bob tries to fetch an article, that certainly does not exist.
        response = self.testapp.get('/i_do_not_exist', expect_errors=True)

        # He receives a 404 and a brief error text.
        self.assertTitleEqual(response, 'MyWiki *** Article not found')
        self.assertEqual(response.status_int, 404)
        self.assertEqual(
            response.pyquery('#error-message').text(), 'Article not found')

        # Top panel is present on the page too.
        self.assertEqual(len(response.pyquery('#top-panel')), 1)

        # There is also a link to the homepage.
        self.assertHasLinkToHomepage(response)

    def logging_out_at_error_page_redirects_to_homepage(self):
        # Bob tries to fetch an article, that certainly does not exist. He
        # receives a 404.
        error_page = self.testapp.get('/i_do_not_exist', expect_errors=True)

        # He clicks a "Sign Out" link and is redirected to homepage as a result.
        response = error_page.click(linkid='logout-link').follow()
        self.assertTitleEqual(response, u'MyWiki — Welcome to MyWiki!')

    def test_404_page_offers_user_to_login_or_sign_up(self):
        # Bob tries to fetch an article, that certainly does not exist. He
        # receives a 404.
        error_page = self.testapp.get('/i_do_not_exist', expect_errors=True)

        # However, he sees, that page offers him to log in or sign up to create
        # the article he requested.
        auth_offer = error_page.pyquery('#error-detail')
        self.assertTrue(bool(auth_offer))
        self.assertEqual(
            auth_offer.text(),
            'Sign in or sign up to create the article you requested.')

        # There are two links in the offer, that lead to corresponding pages.
        self.assertHasLink(error_page, '#login-offer-link', text='Sign in')
        self.assertHasLink(error_page, '#signup-offer-link', text='sign up')

    def test_sign_up_as_offered_by_404_end_up_creating_that_missing_page(self):
        # Bob tries to fetch an article, that certainly does not exist. He
        # receives a 404.
        error_page = self.testapp.get('/i_do_not_exist', expect_errors=True)

        # He sees, that page offers him to log in or sign up to create the
        # article he requested. He chooses to sign up.
        signup_page = error_page.click(linkid='signup-offer-link')

        # Bob signs up.
        form = self.fill_form(
            signup_page, username='bob', password='test123', verify='test123')
        response = form.submit().follow()

        # Browser delivers him the edit page of an article, he was looking for
        # in the first place.
        edit_form = response.form
        self.assertTitleEqual(response, 'MyWiki *** New Article')
        self.assertEqual(edit_form['head'].value, 'I Do Not Exist')
        self.assertEqual(edit_form['body'].value, '')

    def test_login_as_offered_by_404_end_up_creating_that_missing_page(self):
        # Bob signs up and immediately logs out.
        self.sign_up()
        self.testapp.get('/logout')

        # He tries to fetch an article, that certainly does not exist, and
        # receives a 404.
        error_page = self.testapp.get('/those_cozy_sharks', expect_errors=True)

        # He sees, that page offers him to log in or sign up to create the
        # article he requested. Since he's an existing user, Bob opts for login.
        login_page = error_page.click(linkid='login-offer-link')

        # Bob logs in.
        form = self.fill_form(login_page, username='bob', password='test123')
        response = form.submit().follow()

        # Browser delivers him the edit page of an article, he was looking for
        # in the first place.
        edit_form = response.form
        self.assertTitleEqual(response, 'MyWiki *** New Article')
        self.assertEqual(edit_form['head'].value, 'Those Cozy Sharks')
        self.assertEqual(edit_form['body'].value, '')

    def test_404_page_has_no_history_link(self):
        # Bob tries to fetch an article, that certainly does not exist. He
        # receives a 404.
        error_page = self.testapp.get('/dont_open_me', expect_errors=True)

        # He notices, that this page does not have a link to history.
        history_link = error_page.pyquery('a#history-link')
        self.assertFalse(bool(history_link))


class SingleVersionDeleteAttemptErrorPageTest(BaseTestCase):
    def test_error_page_displays_correctly_for_logged_in_user(self):
        # Bob sings up and immediately creates an article.
        self.create_article('/cyan')
        ver_id = self.fetch_version_ids('/cyan')[0]

        # After that he tries to delete article's single version by direct url.
        response = self.testapp.get(
            '/_delete/cyan/_version/{}'.format(ver_id), expect_errors=True)

        # Error page is displayed to him. This page has bob's name, link to
        # homepage and link to logout handler.
        username = response.pyquery('span#username')
        homepage_link = response.pyquery('a#homepage-link')
        logout_link = response.pyquery('a#logout-link')

        self.assertTrue(bool(username))
        self.assertTrue(bool(homepage_link))
        self.assertTrue(bool(logout_link))

        self.assertEqual(username.text(), 'bob')