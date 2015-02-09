# coding=utf-8
from base import BaseTestCase


class BasicViewPageTest(BaseTestCase):
    def test_there_is_a_link_to_homepage_on_any_wiki_page(self):
        # Bob signs up and immediately creates a new article.
        self.sign_up()
        edit_page = self.testapp.get('/kittens').follow()
        
        # He saves the article with the default values, that are already present
        # in the form.
        self.fill_form(edit_page).submit()
        
        # Bob opens newly created article.
        new_article = self.testapp.get('/kittens')

        # There's a link to app's homepage.
        self.assertHasLinkToHomepage(new_article)
        
    def test_there_is_a_link_to_homepage_even_for_unauthorized_users(self):
        # Bob signs up and immediately creates a new article.
        self.sign_up()
        edit_page = self.testapp.get('/kittens').follow()
        
        # He saves the article with the default values, that are already present
        # in the form. Then, Bob signs out.
        self.fill_form(edit_page).submit()
        self.testapp.get('/logout')
        
        # Bob opens newly created article.
        new_article = self.testapp.get('/kittens')
        
        # There's a link to app's homepage.
        self.assertHasLinkToHomepage(new_article)

    def test_logging_out_on_view_page_redirects_back_there(self):
        # Bob signs up and immediately creates a new article.
        self.sign_up()
        edit_form = self.testapp.get('/kittens').follow()

        # He saves the article with the default values. He is redirected to the
        # new article.
        new_article = self.fill_form(edit_form).submit().follow()

        # Bob signs out. Upon doing this, he is redirected back to 'Kittens'
        # article.
        response = new_article.click(linkid='logout-link').follow()
        self.assertTitleEqual(response, u'MyWiki — Kittens')

    def test_there_is_a_link_to_history_page_above_every_article(self):
        # Bob signs up and immediately creates a new article.
        self.sign_up()
        edit_form = self.testapp.get('/kittens').follow()

        # He saves the article with the default values. He is redirected to the
        # new article.
        new_article = self.fill_form(edit_form).submit().follow()

        # There is a link to the history page for this article in navigation
        # panel.
        self.assertHasLink(
            new_article, '#history-link', text='History',
            href='/_history/kittens')
