# coding=utf-8
from datetime import datetime
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

    def test_the_only_version_is_labeled_both_current_and_new_article(self):
        # Bob signs up and creates a new article.
        new_article = self.create_article('/one_more_step')

        # Bob clicks on "History" link and browser delivers him the history
        # page for the article.
        history_page = new_article.click(linkid='history-link')

        # There is only one version on this page. It is labeled as both, "new
        # page" and "current".
        labels = history_page.pyquery('.distinction-label')
        self.assertEqual(len(labels), 2)
        self.assertIn('(new article)', labels.text())
        self.assertIn('(current)', labels.text())

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

    def test_version_ts_doesnt_have_a_leading_0_in_days_less_than_10(self):
        # Bob signs up and creates an article.
        self.create_article('/tardis')

        # Suddenly, time shifts! It is 7th March 2001!
        article_obj = self.article_model.all().get()
        fv = article_obj.first_version
        fv.created = datetime(day=7, month=3, year=2001)
        fv.put()

        # Bob opens the history page for newly created article.
        new_article = self.testapp.get('/_history/tardis')

        # There is one version on history page for this article. It has a
        # timestamp in which days are expressed with one-digit number. That's
        # it: without leading zero!
        ts = new_article.pyquery('.timestamp')
        self.assertTrue(ts.text().startswith('7'))


class HistoryActionsTest(BaseTestCase):
    def test_versions_are_displayed_with_links_to_view_them(self):
        # Bob signs up and creates a new article.
        self.create_article('/time_has_come')

        # He edits it several times to create more versions.
        self.edit_article('/time_has_come', head='This Is The End')
        self.edit_article('/time_has_come', body='<p>Are you ready?</p>')
        self.edit_article('/time_has_come', head='The Day Of Wrath')

        urls_from_db = [
            '/time_has_come/_version/{}'.format(vid) for vid in
            self.fetch_version_ids('/time_has_come')]

        # Bob opens article's history page. It lists four versions, each has a
        # link to view page.
        history_page = self.testapp.get('/_history/time_has_come')
        page_links_to_versions = history_page.pyquery('.version-view-link')
        urls_from_page = [p.attrib['href'] for p in page_links_to_versions]

        self.assertEqual(len(page_links_to_versions), 4)
        self.assertSetEqual(set(urls_from_db), set(urls_from_page))

        link_text = page_links_to_versions[0].text
        self.assertEqual(link_text, 'view')

    def test_homepage_view_version_links_work(self):
        # Bob signs up and goes to home page to initialize it.
        self.sign_up()
        self.testapp.get('/')

        # He edits homepage to add a new version to it. After that he goes to
        # homepage's history page.
        homepage = self.edit_article('/', head='Get The Hell Out Of Here!')
        history_page = homepage.click(linkid='history-link')

        # There are two links on history page.
        urls = [
            link.attrib['href']
            for link in history_page.pyquery('a.version-view-link')]
        self.assertEqual(len(urls), 2)

        # Both of them work: requesting them delivers page with correct
        # content.
        version_1 = self.testapp.get(urls[0])
        self.assertTitleEqual(version_1, u'MyWiki — Get The Hell Out Of Here!')
        head = version_1.pyquery('#wiki-head')
        self.assertEqual(head.text(), 'Get The Hell Out Of Here!')

        version_2 = self.testapp.get(urls[1])
        self.assertTitleEqual(version_2, u'MyWiki — Welcome to MyWiki!')
        head = version_2.pyquery('#wiki-head')
        self.assertEqual(head.text(), 'Welcome to MyWiki!')

    def test_versions_are_displayed_with_links_to_edit_them(self):
        # Bob signs up and creates a new article.
        self.create_article('/test')

        # He edits the page several times to make new versions.
        self.edit_article('/test', head='Check')
        self.edit_article('/test', body='<span>Some filler text.</span>')
        self.edit_article('/test', body='<p>Imagination has broken.</p>')

        urls_from_db = [
            '/_edit/test/_version/{}'.format(vid) for vid in
            self.fetch_version_ids('/test')]

        # Bob opens article's history page. It lists four versions, each has a
        # link to edit page.
        history_page = self.testapp.get('/_history/test')
        page_links_to_versions = history_page.pyquery('.version-edit-link')
        urls_from_page = [p.attrib['href'] for p in page_links_to_versions]

        self.assertEqual(len(page_links_to_versions), 4)
        self.assertSetEqual(set(urls_from_db), set(urls_from_page))

        link_text = page_links_to_versions[0].text
        self.assertEqual(link_text, 'edit')

    def test_homepage_edit_version_links_work(self):
        # Bob signs up and goes to home page to initialize it.
        self.sign_up()
        self.testapp.get('/')

        # He edits homepage to add a new version to it. After that he goes to
        # homepage's history page.
        homepage = self.edit_article('/', head='So Good To See You Here!')
        history_page = homepage.click(linkid='history-link')

        # There are two links on history page.
        urls = [
            link.attrib['href']
            for link in history_page.pyquery('a.version-edit-link')]
        self.assertEqual(len(urls), 2)

        # Both of them work: requesting them delivers page with correct
        # content.
        version_1 = self.testapp.get(urls[0])
        self.assertTitleEqual(
            version_1, u'MyWiki — So Good To See You Here! (edit)')
        form = version_1.form
        self.assertEqual(form['head'].value, 'So Good To See You Here!')

        version_2 = self.testapp.get(urls[1])
        self.assertTitleEqual(version_2, u'MyWiki — Welcome to MyWiki! (edit)')
        form = version_2.form
        self.assertEqual(form['head'].value, 'Welcome to MyWiki!')

    def test_versions_are_displayed_with_links_to_delete_them(self):
        # Bob signs up and creates an article. He edits it several times to make
        # more versions.
        self.create_article('/red')
        self.edit_article('/red', body='<p>Like blood.</p>')
        self.edit_article('/red', body='<p>Like roses.</p>')

        urls_from_db = [
            '/_delete/red/_version/{}'.format(vid)
            for vid in self.fetch_version_ids('/red')]

        # Bob goes to new article's history page. There are three entries. All
        # of them have a "delete" link associated with them.
        history_page = self.testapp.get('/_history/red')
        urls_from_page = [
            link.attrib['href']
            for link in history_page.pyquery('a.version-delete-link')]

        self.assertEqual(len(urls_from_page), 4)
        self.assertSetEqual(set(urls_from_db), set(urls_from_page))

        link_text = history_page.pyquery('a.version-delete-link')[0].text()
        self.assertEqual(link_text, 'delete')

    def test_delete_link_is_not_displayed_for_the_only_version(self):
        # Bob signs up and creates a new article.
        self.create_article('/green')

        # He opens article's history page. There is only one entry. There is no
        # "delete" link near to it since it is the only version of this article.
        history_page = self.testapp.get('/_history/green')

        self.assertRaises(
            AssertionError, self.assertHasLink, history_page,
            'a.version-delete-link')

    def test_delete_link_is_not_displayed_for_unauthorized_users(self):
        # Bob signs up and creates a new article. He edits it several times to
        # make more versions.
        self.create_article('/blue')
        self.edit_article('/blue', body='<p>Like sky.</p>')
        self.edit_article('/blue', body='<p>Like her eyes.</p>')

        # Bob sings out and immediately opens the history page for the article.
        self.testapp.get('/logout')
        history_page = self.testapp.get('/_history/green')

        # There are no "delete" links present at all.
        self.assertRaises(
            AssertionError, self.assertHasLink, history_page,
            'a.version-delete-link')

    def test_homepage_delete_version_links_work(self):
        # Bob signs up and immediately edits MyWiki's homepage to initialize it
        # and to create one more version of it.
        self.sign_up()
        self.edit_article('/', title='Welcome to YourWiki!')

        # Bob then opens the history page. There are two versions, each has
        # "delete" links.
        history_page = self.testapp.get('/_history/')
        delete_links = history_page.pyquery('a.version-delete-link')
        self.assertEqual(len(delete_links), 2)

        # Those links work.
        history_page.click(description='delete', index=0)
        version_ids = self.fetch_version_ids('/')
        self.assertEqual(len(version_ids), 1)