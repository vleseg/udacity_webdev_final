# coding=utf-8
from datetime import datetime, timedelta
# Internal project imports
from base import BaseTestCase
from model import Article


# TODO: write a test about version's timestamp -- it has to be correct
class BasicHistoryPageTest(BaseTestCase):
    def test_there_is_a_history_page_for_every_article(self):
        # Bob opens MyWiki's homepage. There is a link to the edit history page.
        homepage = self.testapp.get('/')
        self.assertHasLink(
            homepage, '#history-link', text='History', href='/_history/')

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
        self.assertHasLink(
            new_article, '#history-link', text='History',
            href='/_history/kittens')
        history_page = new_article.click(linkid='history-link')

        # History page is delivered to Bob. It has an indicative title.
        self.assertEqual(history_page.status_int, 200)
        self.assertTitleEqual(
            history_page, u'MyWiki — Kittens (history)')


class HistoryUnitTests(BaseTestCase):
    def test_version_timestamp_stores_a_correct_value(self):
        # Bob sings up and immediately creates a new article.
        self.sign_up()
        new_page = self.testapp.get('/_edit/kittens')

        # He saves article with default values.
        t = datetime.utcnow()
        self.fill_form(new_page).submit()

        # Timestamp for article's first version is written correctly.
        version_ts = Article.latest_version('/kittens').modified
        self.assertAlmostEqual(t, version_ts, delta=timedelta(seconds=1))