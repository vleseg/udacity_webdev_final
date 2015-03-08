# coding=utf-8
from datetime import datetime, timedelta
from random import randint
from time import sleep
# Internal project imports
from base import BaseTestCase


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

        # After a while Bob edits the article two times with a little pause
        # between edits.
        self.edit_article(
            '/so_where_do_we_begin',
            body='<span>And what else can we say?</span>')
        sleep(1)
        article = self.edit_article(
            '/so_where_do_we_begin', head='Drifting In And Out')
        t = datetime.utcnow()

        # Version timestamp on page shows timestamp of article's last
        # modification (i. e. current version creation date and time).
        ts = article.pyquery('#ts-version>.timestamp')
        ts_parsed = datetime.strptime(ts.text(), '%d %B %Y, %H:%M:%S')
        self.assertAlmostEqual(t, ts_parsed, delta=timedelta(1))

    def test_another_version_of_article_displays_with_current_timestamp(self):
        # Bob signs up and creates a new article.
        self.create_article('/wag_the_dog')
        t = datetime.utcnow()
        sleep(1)

        # He creates several versions of article with short delays between them.
        self.edit_article('/wag_the_dog', head='Wag The Wig')
        t2 = datetime.utcnow()
        sleep(1)
        self.edit_article('/wag_the_dog', head='Dig The Big')
        sleep(1)

        version_ids = self.fetch_version_ids('/wag_the_dog')

        # Bob consecutively opens article's first and second versions by direct
        # urls. Timestamps on page in both cases indicate time, when
        # corresponding version was created.
        first_version = self.testapp.get(
            '/wag_the_dog/_version/{}'.format(version_ids[0]))
        ts = first_version.pyquery('#ts-version>.timestamp')
        ts_parsed = datetime.strptime(ts.text(), '%d %B %Y, %H:%M:%S')
        self.assertAlmostEqual(t, ts_parsed, delta=timedelta(1))

        seconds_version = self.testapp.get(
            '/wag_the_dog/_version/{}'.format(version_ids[1]))
        ts = seconds_version.pyquery('#ts-version>.timestamp')
        ts_parsed = datetime.strptime(ts.text(), '%d %B %Y, %H:%M:%S')
        self.assertAlmostEqual(t2, ts_parsed, delta=timedelta(1))

    def test_version_ts_for_newly_created_article_is_labeled_new(self):
        # Bob signs up and creates a new article.
        new_article = self.create_article('/its_nothing')

        # There's a version timestamp on view page for newly created article.
        # It is labeled "new article".
        label = new_article.pyquery('.distinction-label')
        self.assertTrue(bool(label))
        ts = new_article.pyquery('#ts-version')
        self.assertIn('(new article)', ts.text())

    def test_version_ts_for_any_article_is_labeled_current(self):
        # Bob signs up and creates a new article.
        new_article = self.create_article('/horses')

        # There's a version timestamp on view page for newly created article.
        # It is labeled "current".
        label = new_article.pyquery('.distinction-label')
        self.assertTrue(bool(label))
        ts = new_article.pyquery('#ts-version')
        self.assertIn('(current)', ts.text())

        # Bob creates another article.
        self.create_article('/cows', sign_up=False)

        # He edits it several times to make more versions.
        self.edit_article('/cows', head='Goats')
        second_article = self.edit_article(
            '/cows', body='<span>Mere cattle.</span>')

        # There's a version timestamp on view page for the modified article. It
        # is labeled "current".
        label = second_article.pyquery('.distinction-label')
        self.assertTrue(bool(label))
        ts = new_article.pyquery('#ts-version')
        self.assertIn('(current)', ts.text())

    def test_version_ts_for_first_version_of_the_article_is_labeled_new(self):
        # Bob signs up and creates a new article.
        self.create_article('/viz_a_viz')

        # He edits the article several times to make more versions.
        self.edit_article('/viz_a_viz', body="C'est la vie!")
        self.edit_article('/viz_a_viz', head='Bonjour!')

        first_version_id = self.fetch_version_ids('/viz_a_viz')[0]

        # Bob opens view page for the very first version of the article.
        first_version_page = self.testapp.get(
            '/viz_a_viz/_version/{}'.format(first_version_id))

        # There's a version timestamp on view page for the modified article. It
        # is labeled "current".
        label = first_version_page.pyquery('.distinction-label')
        self.assertTrue(bool(label))
        ts = first_version_page.pyquery('#ts-version')
        self.assertIn('(new article)', ts.text())

    def test_version_ts_doesnt_have_a_leading_0_in_days_less_than_10(self):
        # Bob sings up and creates an article.
        self.create_article('/back_in_the_future')

        # Suddenly, time shifts! It is 5th January 1990!
        article_obj = self.article_model.all().get()
        fv = article_obj.first_version
        fv.created = datetime(day=5, month=1, year=1990)
        fv.put()

        # Bob opens newly created article.
        new_article = self.testapp.get('/back_in_the_future')

        # There is a version timestamp on article page. Days in it are expressed
        # with one-digit number. That's it: without leading zero!
        ts = new_article.pyquery('#ts-version>.timestamp')
        self.assertTrue(ts.text().startswith('5'))


class VersionsTest(BaseTestCase):
    def test_can_open_view_page_for_different_article_version(self):
        # Bob signs up and creates an article.
        self.create_article('/in_a_timely_manner')

        # Bob edits the article two times to create more versions.
        self.edit_article('/in_a_timely_manner', head='Too Late')
        self.edit_article('/in_a_timely_manner', head='Just In Time')

        version_ids = self.fetch_version_ids('/in_a_timely_manner')

        # Bob consecutively tries to open view pages for different article
        # versions by direct url. He succeeds.
        for vid in version_ids:
            response = self.testapp.get(
                '/in_a_timely_manner/_version/{}'.format(vid))
            self.assertEqual(response.status_int, 200)

    def test_requesting_article_version_by_url_opens_that_version(self):
        # Bob signs up and creates an article.
        self.create_article('/schadenfreude')

        # He edits it several times, so that it has more versions.
        self.edit_article('/schadenfreude', head='Gloating')
        self.edit_article('/schadenfreude', body='Never mind...')
        self.edit_article('/schadenfreude', head='Compassion')

        version_ids = self.fetch_version_ids('/schadenfreude')

        # He gets different versions of article by their direct urls and
        # ensures, that they reflect the timeline of changes correctly.
        first_version = self.testapp.get(
            '/schadenfreude/_version/{}'.format(version_ids[0]))
        fv_head = first_version.pyquery('#wiki-head')
        fv_body = first_version.pyquery('#wiki-body')
        self.assertEqual(fv_head.text(), 'Schadenfreude')
        self.assertEqual(fv_body.text(), '')

        latest_version = self.testapp.get(
            '/schadenfreude/_version/{}'.format(version_ids[-1]))
        lv_head = latest_version.pyquery('#wiki-head')
        lv_body = latest_version.pyquery('#wiki-body')
        self.assertEqual(lv_head.text(), 'Compassion')
        self.assertEqual(lv_body.text(), 'Never mind...')

        one_more_version = self.testapp.get(
            '/schadenfreude/_version/{}'.format(version_ids[2]))
        omv_head = one_more_version.pyquery('#wiki-head')
        omv_body = one_more_version.pyquery('#wiki-body')
        self.assertEqual(omv_head.text(), 'Gloating')
        self.assertEqual(omv_body.text(), 'Never mind...')

    def test_accessing_nonexistent_version_delivers_latest(self):
        # Bob signs up and creates an article.
        self.create_article('/vita_nostra_brevis_est')

        # He edits the article once to create another version.
        self.edit_article('/vita_nostra_brevis_est', head='Brevi Finietur')

        version_ids = self.fetch_version_ids('/vita_nostra_brevis_est')

        random_id = randint(0, 10)
        while random_id in version_ids:
            random_id = randint(0, 10)

        # Bob tries to fetch article's version, which does not exist by direct
        # url.
        response = self.testapp.get(
            '/vita_nostra_brevis_est/_version/{}'.format(random_id))

        # Current version is delivered to him.
        self.assertTitleEqual(response, u'MyWiki — Brevi Finietur')