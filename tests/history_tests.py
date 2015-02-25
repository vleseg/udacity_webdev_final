# coding=utf-8
from datetime import datetime
from time import sleep
# Internal project imports
from base import BaseTestCase


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

        # Bob signs up and creates an article.
        new_article = self.create_article('/kittens')

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
        # Bob signs up and creates a new article.
        new_article = self.create_article('/russia_strong')

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
        # Bob signs up and creates a new article.
        new_article = self.create_article('/white_rabbit')

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
    def test_history_page_has_a_link_to_edit_articles_current_version(self):
        # Bob signs up and creates a new article with a short body.
        self.create_article(
            '/dancing_queen',
            body='<p>You can dance, you can jive, having the time of your '
                 'life. See that girl, watch that scene, dig in the Dancing '
                 'Queen.</p>')

        # After a short delay he opens an edit page for the article and clears
        # article's body.
        sleep(1)
        self.edit_article('/dancing_queen', body='')

        # The he opens the history page.
        history_page = self.testapp.get('/_history/dancing_queen')

        # History page has an "Edit Article" link in navigation panel at the
        # top of the page.
        self.assertHasLink(history_page, '#edit-article-link')

        # Bob clicks the link. Browser delivers him the article's edit page.
        edit_page = history_page.click(linkid='edit-article-link')
        self.assertTitleEqual(edit_page, u'MyWiki — Dancing Queen (edit)')

        # Article's body is empty, because it is the current version.
        self.assertEqual(edit_page.form['body'].value, '')

    def test_first_version_on_history_page_is_labeled_new_article(self):
        # Bob signs up and creates a new article.
        self.create_article('/no_nay_never_no_more')

        # Bob edits article's body and saves it. Then he opens the history page.
        self.edit_article('/no_nay_never_no_more', body='<span>Bogus!</span>')
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
        # Bob signs up and creates a new article.
        self.create_article('/remember_remember')

        # Bob edits article's body and saves it. Then he opens the history page.
        self.edit_article(
            '/remember_remember', body='<p>the fifth of november</p>')
        history_page = self.testapp.get('/_history/remember_remember')

        # History page has two versions. The top one is the newest one. It is
        # labeled "(current)".
        versions_list = history_page.pyquery('ul#versions>li')
        newest_version = versions_list.eq(0)
        label = newest_version.find('.distinction-label')
        self.assertEqual(len(label), 1)
        self.assertEqual(label.text(), '(current)')

    def test_version_timestamp_is_human_readable(self):
        # Bob signs up and creates a new article.
        self.create_article('/cogito_ergo_sum')

        # He opens article's history page.
        history_page = self.testapp.get('/_history/cogito_ergo_sum')

        # There's one version on the page. It contains timestamp of format
        # "1 January 2015, 17:00:09".
        version_timestamp = history_page.pyquery('.timestamp')
        self.assertEqual(len(version_timestamp), 1)
        self.assertTrue(
            bool(datetime.strptime(
                version_timestamp.text(), '%d %B %Y, %H:%M:%S')))

    def test_versions_are_displayed_with_links_to_view_them(self):
        # Bob signs up and creates a new article.
        self.create_article('/time_has_come')

        # He edits it several times to create more versions.
        self.edit_article('/time_has_come', head='This Is The End')
        sleep(0.1)
        self.edit_article('/time_has_come', body='<p>Are you ready?</p>')
        sleep(0.1)
        self.edit_article('/time_has_come', head='The Day Of Wrath')

        urls_from_db = [
            '/time_has_come/_version/{}'.format(vid) for vid in
            self.fetch_version_ids('/time_has_come')]

        # Bob opens article's history page. It lists four versions, each has a
        # link to view page.
        history_page = self.testapp.get('/_history/time_has_come')
        page_links_to_versions = history_page.pyquery(
            '#versions>li>.version-view-link')
        urls_from_page = [p.attrib['href'] for p in page_links_to_versions]

        self.assertEqual(len(page_links_to_versions), 4)
        self.assertSetEqual(set(urls_from_db), set(urls_from_page))

        link_text = page_links_to_versions[0].text
        self.assertEqual(link_text, 'view')