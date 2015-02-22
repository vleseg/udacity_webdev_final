# coding=utf-8
from datetime import datetime, timedelta
from time import sleep
# Internal project imports
from base import BaseTestCase
from model import Article


class BasicViewPageTest(BaseTestCase):
    def test_there_is_a_link_to_homepage_on_any_wiki_page(self):
        # Bob signs up and  creates a new article.
        self.create_article('/kittens')
        
        # Bob opens newly created article.
        new_article = self.testapp.get('/kittens')

        # There's a link to app's homepage.
        self.assertHasLinkToHomepage(new_article)
        
    def test_there_is_a_link_to_homepage_even_for_unauthorized_users(self):
        # Bob signs up and creates a new article and then signs out.
        self.create_article('/kittens')
        self.testapp.get('/logout')
        
        # Bob opens newly created article.
        new_article = self.testapp.get('/kittens')
        
        # There's a link to app's homepage.
        self.assertHasLinkToHomepage(new_article)

    def test_logging_out_on_view_page_redirects_back_there(self):
        # Bob signs up and creates a new article.
        new_article = self.create_article('/swag')

        # Bob signs out. Upon doing this, he is redirected back to 'Kittens'
        # article.
        response = new_article.click(linkid='logout-link').follow()
        self.assertTitleEqual(response, u'MyWiki — Swag')

    def test_there_is_a_link_to_history_page_above_every_article(self):
        # Bob signs up and creates a new article.
        new_article = self.create_article('/kittens')

        # There is a link to the history page for this article in navigation
        # panel.
        self.assertHasLink(
            new_article, '#history-link', text='History',
            href='/_history/kittens')


class TimestampTest(BaseTestCase):
    def test_there_is_a_timestamp_of_currently_viewed_version(self):
        # Bob signs up and creates a new article.
        new_article = self.create_article('/what_does_the_fox_say')

        # There's a timestamp on the page, which indicates date and time when
        # currently current version (the first one) was created.
        timestamp = new_article.pyquery('#ts-version')
        self.assertTrue(timestamp.text().startswith('Version of '))

    def test_timestamp_of_currently_viewed_version_is_human_readable(self):
        # Bob signs up and creates a new article.
        new_article = self.create_article('/esse_homo')

        # Version timestamp is present on page. It has formatted like
        # "1 January 2015, 17:00:09".
        ts = new_article.pyquery('#ts-version>.timestamp')
        self.assertEqual(len(ts), 1)
        self.assertTrue(
            bool(datetime.strptime(ts.text(), '%d %B %Y, %H:%M:%S')))

    def test_timestamp_really_belongs_to_current_version(self):
        # Bob signs up and creates a new article.
        self.create_article('/so_where_do_we_begin')
        sleep(1)

        # After a while Bob edits the article.
        edit_page = self.testapp.get('/_edit/so_where_do_we_begin')
        self.fill_form(
            edit_page, body="<span>And what else can we say?</span>").submit()
        sleep(1)

        # And again.
        edit_page = self.testapp.get('/_edit/so_where_do_we_begin')
        article = self.fill_form(
            edit_page, head='Drifting In And Out').submit().follow()
        t = datetime.utcnow()

        # Version timestamp on page shows timestamp of article's last
        # modification (i. e. current version creation date and time).
        ts = article.pyquery('#ts-version>.timestamp')
        ts_parsed = datetime.strptime(ts.text(), '%d %B %Y, %H:%M:%S')
        self.assertAlmostEqual(t, ts_parsed, delta=timedelta(1))
    #
    # def test_version_ts_for_newly_created_article_is_labeled_new(self):
    #     # Bob signs up and creates a new article.
    #     new_article = self.create_article('/its_nothing')
    #
    #     # There's a version timestamp on view page for newly created article. It
    #     # is labeled as "new article".
    #     label = new_article.pyquery('.distinction-label')
    #     self.assertTrue(bool(label))
    #     ts = new_article.pyquery('#ts-version')
    #     self.assertIn('(new article)', ts.text())


class VersionsTest(BaseTestCase):
    def test_can_open_view_page_for_different_article_version(self):
        # Bob sings up and creates an article.
        self.create_article('/in_a_timely_manner')
        sleep(0.1)

        # Bob edits the article to create a new version.
        edit_page = self.testapp.get('/_edit/in_a_timely_manner')
        self.fill_form(edit_page, head="Too Late")
        sleep(0.1)

        # ...and once more.
        edit_page = self.testapp.get('/_edit/in_a_timely_manner')
        self.fill_form(edit_page, head='Just In Time!')

        article = Article.by_url('/in_a_timely_manner')
        version_ids = [v.key().id() for v in article.version_set]

        # Bob consecutively tries to open view pages for different article
        # versions by direct url. He succeeds.
        for vid in version_ids:
            response = self.testapp.get(
                '/in_a_timely_manner/_history/{}'.format(vid))
            self.assertEqual(response.status_int, 200)