# coding=utf-8
from random import randint
# Internal project imports
from base import BaseTestCase


class NotFoundErrorPageTest(BaseTestCase):
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

    def test_404_when_del_ver_of_ne_article_offers_to_create_this_article(self):
        # Bob sings up and immediately tries to delete a version of non-existent
        # article by direct url.
        self.sign_up()
        response = self.testapp.get(
            '/_delete/i_do_not_exist/_version/{}'.format(randint(0, 10)),
            expect_errors=True)

        # Of course, he gets an error.
        head = response.pyquery('#error-message')
        self.assertTitleEqual(response, 'MyWiki *** Article not found')
        self.assertEqual(head.text(), 'Article not found')

        # Error message offers Bob to create a new article with the requested
        # url.
        body = response.pyquery('#error-detail')
        offer_link = response.pyquery('a#new-article-offer-link')
        self.assertEqual(
            body.text(), 'You can create this article; click here to do so.')
        self.assertEqual(offer_link.text(), 'click here')
        self.assertEqual(offer_link.attr('href'), '/_edit/i_do_not_exist')


class VersionNotFoundErrorPageTest(BaseTestCase):
    def test_error_page_displays_correctly(self):
        # Bob signs up and creates an article.
        self.create_article('/navy_blue')

        real_version_id = self.fetch_version_ids('/navy_blue')[0]
        fake_version_id = randint(0, 10)
        while real_version_id == fake_version_id:
            fake_version_id = randint(0, 10)

        # Bob tries to delete article's version, which certainly does not exist
        # via direct url. He receives an error page.
        error_page = self.testapp.get(
            '/_delete/navy_blue/_version/{}'.format(fake_version_id),
            expect_errors=True)

        # This page has a correct title and head.
        head = error_page.pyquery('#error-message')
        body = error_page.pyquery('#error-detail')

        self.assertTitleEqual(error_page, 'MyWiki *** Version not found')
        self.assertEqual(head.text(), 'Version not found')
        self.assertEqual(
            body.text(), 'Version with the requested id does not exist.')


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

    def test_error_message_tells_that_you_cant_delete_the_only_version(self):
        # Bob sings up and creates a new article.
        self.create_article('/lone_version')

        ver_id = self.fetch_version_ids('/lone_version')[0]

        # Bob tries to delete article's only version.
        response = self.testapp.get(
            '/_delete/lone_version/_version/{}'.format(ver_id),
            expect_errors=True)

        # The application responds with an error, which tells Bob why he can't
        # delete the version.
        message = response.pyquery('h1#error-message')
        detail = response.pyquery('#error-detail')
        self.assertEqual(message.text(), 'Operation forbidden')
        self.assertEqual(
            detail.text(), "You can't delete article's sole version.")