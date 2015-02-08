# coding=utf-8
from base import BaseTestCase


# TODO: write a test about version's timestamp -- it has to be correct
# TODO [REFACTOR]: extract logic of testing link presence by id to BaseTextCase
# TODO [ADD PREV]: accepted arguments -- id (obligatory), text, url
class BasicHistoryPageTest(BaseTestCase):
    def test_there_is_a_history_page_for_every_article(self):
        # Bob opens MyWiki's homepage. There is a link to the edit history page.
        homepage = self.testapp.get('/')
        history_link = homepage.pyquery('#history-link')
        self.assertTrue(bool(history_link))

        # Bob clicks the link and edit history of the homepage is delivered to
        # him. The page has an indicative title.
        history_page = homepage.click(linkid='history-link')
        self.assertEqual(history_page.status_int, 200)
        self.assertTitleEqual(
            history_page, u'MyWiki — Welcome to MyWiki! (history)')

        # Bob signs up and creates an article right away.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/kittens')

        # He saves the article with default values. Webapp redirects him to
        # the newly created article.
        new_article = self.fill_form(edit_page).submit().follow()

        # There is a link to edit history page. Bob clicks that link.
        history_link = new_article.pyquery('#history-link')
        self.assertTrue(bool(history_link))
        history_page = new_article.click(linkid='history-link')

        # History page is delivered to Bob. It has an indicative title.
        self.assertEqual(history_page.status_int, 200)
        self.assertTitleEqual(
            history_page, u'MyWiki — Kittens (history)')