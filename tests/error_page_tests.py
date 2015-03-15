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

        fake_version_id = self.get_fake_version_id('/navy_blue')

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

    def test_redirect_to_latest_version_when_logging_out_of_error_page(self):
        # Bob signs up and creates an article. He edits it several times to add
        # more versions.
        self.create_article('/flowers')
        self.edit_article('/flowers', body='<div>Roses are red.</div>')
        self.edit_article('/flowers', body='<div>Violets are blue.</div>')

        fake_version_id = self.get_fake_version_id('/flowers')

        # Bob tries to delete article's nonexistent version via direct url.
        error_page = self.testapp.get(
            '/_delete/flowers/_version/{}'.format(fake_version_id),
            expect_errors=True)

        # An error is served him. He logs out from that page.
        response = error_page.click(linkid='logout-link').follow()

        # Bob is redirected to article's latest version.
        head = response.pyquery('#wiki-head')
        body = response.pyquery('#wiki-body')
        self.assertTitleEqual(response, u'MyWiki — Flowers')
        self.assertEqual(head.text(), 'Flowers')
        self.assertEqual(body.text(), 'Violets are blue.')


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

    def test_redirect_to_latest_version_when_logging_out_of_error_page(self):
        # Bob signs up and creates an article.
        self.create_article('/ping', body='<h2>Pong!</h2>')

        version_id = self.fetch_version_ids('/ping')[0]

        # Bob tries to delete article's only version via direct url.
        error_page = self.testapp.get(
            '/_delete/ping/_version/{}'.format(version_id), expect_errors=True)

        # An error is served him. He logs out from that page.
        response = error_page.click(linkid='logout-link').follow()

        # Bob is redirected to article's latest version.
        head = response.pyquery('#wiki-head')
        body = response.pyquery('#wiki-body')
        self.assertTitleEqual(response, u'MyWiki — Ping')
        self.assertEqual(head.text(), 'Ping')
        self.assertEqual(body.text(), 'Pong!')


class UnauthorizedDeleteAttemptErrorTest(BaseTestCase):
    def test_error_message_offers_unauthorized_user_to_sign_up_or_login(self):
        # Bob sings up and creates a new article. He edits it to add a spare
        # version.
        self.create_article('/people')
        self.edit_article('/people', body='<div>All so different.</div>')

        version_ids = self.fetch_version_ids('/people')

        # Bob signs out and tries to delete one of article's version via direct
        # url.
        self.testapp.get('/logout')
        error_page = self.testapp.get(
            '/_delete/people/_version/{}'.format(version_ids[0]),
            expect_errors=True)

        # Error page is served for Bob.
        head = error_page.pyquery('#error-message')
        body = error_page.pyquery('#error-detail')
        self.assertTitleEqual(error_page, 'MyWiki *** Operation forbidden')
        self.assertEqual(head.text(), 'Operation forbidden')
        self.assertEqual(
            body.text(),
            "This operation is not allowed for unauthorized users. Sign up or "
            "sign in and try again.")

        # Detailed error message contains links to sign up and login page.
        signup_offer_link = error_page.pyquery('#signup-offer-link')
        login_offer_link = error_page.pyquery('a#login-offer-link')

        self.assertEqual(signup_offer_link.text(), 'Sign up')
        self.assertEqual(login_offer_link.text(), 'sign in')
        response_1 = error_page.click(linkid='signup-offer-link')
        response_2 = error_page.click(linkid='login-offer-link')

        self.assertTitleEqual(response_1, 'MyWiki *** Sign Up')
        self.assertTitleEqual(response_2, 'MyWiki *** Login')

    def test_redirect_to_latest_version_after_sign_up_via_error_page_link(self):
        # Bob signs up and creates a new article. He edits it a couple of times
        # to make more versions.
        self.create_article(
            '/keep_talking', body="<p>There's a silence surrounding me</p>")
        self.edit_article(
            '/keep_talking', body="<p>I can't seem to think straight</p>")
        self.edit_article(
            '/keep_talking', body="<p>I'll sit in the corner</p>")

        version_ids = self.fetch_version_ids('/keep_talking')

        # He signs out and tries to delete one of article's versions via direct
        # url. An error page is served. He clicks a "Sign up" link on that page.
        self.testapp.get('/logout')
        response = self.testapp.get(
            '/_delete/keep_talking/_version/{}'.format(version_ids[0]),
            expect_errors=True)
        signup_page = response.click(linkid='signup-offer-link')

        # On sighup page, Bob registers again as another person.
        response = self.fill_form(
            signup_page, username='claudia', password='test',
            verify='test').submit().follow()

        # Bob (or Claudia) is redirected back to "Keep Talking" page -- namely
        # to its latest version.
        head = response.pyquery('#wiki-head')
        body = response.pyquery('#wiki-body')
        self.assertTitleEqual(response, u'MyWiki — Keep Talking')
        self.assertEqual(head.text(), 'Keep Talking')
        self.assertEqual(body.text(), "I'll sit in the corner")

    def test_redirect_to_latest_version_after_login_via_error_page_link(self):
        # Bob signs up and creates a new article. He edits it a couple of times
        # to make more versions.
        self.create_article(
            '/black', body="<span>Like northern night.</span>")
        self.edit_article(
            '/black', body="<span>Like sinner's heart.</span>")
        self.edit_article(
            '/black', body="<span>Like my funeral suit.</span>")

        version_ids = self.fetch_version_ids('/black')

        # He signs out and tries to delete one of article's versions via direct
        # url. An error page is served. He clicks a "sign in" link on that page.
        self.testapp.get('/logout')
        response = self.testapp.get(
            '/_delete/black/_version/{}'.format(version_ids[0]),
            expect_errors=True)
        login_page = response.click(linkid='login-offer-link')

        # On login page, Bob authenticates in the app again.
        response = self.fill_form(
            login_page, username='bob', password='test123').submit().follow()

        # Bob (or Claudia) is redirected back to "Keep Talking" page -- namely
        # to its latest version.
        head = response.pyquery('#wiki-head')
        body = response.pyquery('#wiki-body')
        self.assertTitleEqual(response, u'MyWiki — Black')
        self.assertEqual(head.text(), 'Black')
        self.assertEqual(body.text(), "Like my funeral suit.")