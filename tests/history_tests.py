# coding=utf-8
from datetime import datetime, timedelta
# Internal project imports
from base import BaseTestCase
from model import Article


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

    def test_first_version_of_homepage_can_be_found_on_its_history_page(self):
        # Bob opens MyWiki's homepage.
        homepage = self.testapp.get('/')

        # He clicks the "History" link to see homepage's edit history.
        response = homepage.click(linkid='history-link')

        # History page is delivered to Bob. It has a list of all version of the
        # homepage.
        versions_list = response.pyquery('ul#versions')
        self.assertTrue(bool(versions_list))

        # At the time being it contains only one version.
        versions = versions_list.find('li')
        self.assertEqual(len(versions), 1)

    def test_first_version_of_any_page_can_be_found_on_its_history_page(self):
        # Bob signs up and immediately creates a new article.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/russia_strong')

        # He saves the article with default values. Newly created article is
        # delivered to Bob.
        new_article = self.fill_form(edit_page).submit().follow()

        # He clicks the "History" link to see article's edit history.
        history_page = new_article.click(linkid='history-link')

        # History page is delivered to Bob. It has a list of all version of the
        # article.
        versions_list = history_page.pyquery('ul#versions')
        self.assertTrue(bool(versions_list))

        # At the time being it contains only one version.
        versions = versions_list.find('li')
        self.assertEqual(len(versions), 1)

    def test_after_page_was_edited_new_version_is_created(self):
        # Bob signs up and immediately creates a new article.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/white_rabbit')

        # He saves the article with default values. Newly created article is
        # delivered to Bob.
        new_article = self.fill_form(edit_page).submit().follow()

        # Bob clicks "Edit Article" link. Edit page opens again.
        edit_page = new_article.click(linkid='edit-article-link')

        # Bob changes article's body and saves the page. Modified article is
        # delivered to Bob.
        modified_article = self.fill_form(
            edit_page, body="<p>Follow it, Neo!</p>").submit().follow()

        # He clicks the "History" link to see article's edit history. History
        # page is delivered to Bob.
        history_page = modified_article.click(linkid='history-link')

        # There are two versions of the article present.
        versions = history_page.pyquery('ul#versions>li')
        self.assertEqual(len(versions), 2)


class HistoryPageLayoutTest(BaseTestCase):
    def test_first_version_on_history_page_is_labeled_new_article(self):
        # Bob sings up and immediately creates a new article.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/no_nay_never_no_more')

        # He saves the article with default values. And then opens it for
        # editing again.
        self.fill_form(edit_page).submit()
        edit_page = self.testapp.get('/_edit/no_nay_never_no_more')

        # Bob edits article's body and saves it. Then he opens the history page.
        self.fill_form(edit_page, body='<span>Bogus!</span>').submit()
        history_page = self.testapp.get('/_history/no_nay_never_no_more')

        # History page has two versions.
        versions_list = history_page.pyquery('ul#versions>li')
        self.assertEqual(len(versions_list), 2)

        # The bottom one is the oldest one. It is labeled "(new article)".
        oldest_version = versions_list.eq(1)
        label = oldest_version.find('.distinction-label')
        self.assertEqual(len(label), 1)
        self.assertEqual(label.text(), '(new article)')

    def test_last_version_on_history_page_is_labeled_current(self):
        # Bob sings up and immediately creates a new article.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/remember_remember')

        # He saves the article with default values. And then opens it for
        # editing again.
        self.fill_form(edit_page).submit()
        edit_page = self.testapp.get('/_edit/remember_remember')

        # Bob edits article's body and saves it. Then he opens the history page.
        self.fill_form(edit_page, body='<p>the fifth of november</p>')
        history_page = self.testapp.get('/_history/remember_remember')

        # History page has two versions. The top one is the newest one. It is
        # labeled "(current)".
        versions_list = history_page.pyquery('ul#versions>li')
        newest_version = versions_list.eq(0)
        label = newest_version.find('.distinction-label')
        self.assertEqual(len(label), 1)
        self.assertEqual(label.text(), '(new article)')

    def test_version_timestamp_is_human_readable(self):
        # Bob signs up and immediately creates a new article.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/cogito_ergo_sum')

        # He saves the article with default values.
        self.fill_form(edit_page).submit()

        # Bob opens article's history page.
        history_page = self.testapp.get('/_history/cogito_ergo_sum')

        # There's one version on the page. It contains timestamp of format
        # "1 January 2015, 17:00:09".
        version_timestamp = history_page.pyquery('.timestamp')
        self.assertEqual(len(version_timestamp), 1)
        self.assertFalse(
            self.assertRaises(
                ValueError, datetime.strptime, version_timestamp.text(),
                '%d %B %Y, %H:%M:%S'))


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