# coding=utf-8
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

    def test_timestamp_of_currently_viewed_version_is_correct(self):
        pass