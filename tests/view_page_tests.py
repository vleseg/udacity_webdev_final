# coding=utf-8
from base import BaseTestCase


class BasicViewPageTest(BaseTestCase):
    def test_there_is_a_link_to_homepage_on_any_wiki_page(self):
        # Bob signs up and immediately creates a new page.
        self.sign_up()
        new_page_edit_form = self.testapp.get('/kittens').follow()
        
        # He saves the page with the default values, that are already present
        # in the form.
        self.fill_form(new_page_edit_form).submit()
        
        # Bob opens newly created page.
        new_page = self.testapp.get('/kittens')

        # There's a link to app's homepage.
        self.assertHasLinkToHomepage(new_page)
        
    def test_there_is_a_link_to_homepage_even_for_unauthorized_users(self):
        # Bob signs up and immediately creates a new page.
        self.sign_up()
        new_page_edit_form = self.testapp.get('/kittens').follow()
        
        # He saves the page with the default values, that are already present
        # in the form. Then, Bob signs out.
        self.fill_form(new_page_edit_form).submit()
        self.testapp.get('/logout')
        
        # Bob opens newly created page.
        new_page = self.testapp.get('/kittens')
        
        # There's a link to app's homepage.
        self.assertHasLinkToHomepage(new_page)

    def test_logging_out_while_viewing_page_redirects_back_to_that_page(self):
        # Bob signs up and immediately creates a new page.
        self.sign_up()
        new_page_edit_form = self.testapp.get('/kittens').follow()

        # He saves the page with the default values, that are already present
        # in the form. He is redirected to the new page.
        new_page = self.fill_form(new_page_edit_form).submit().follow()

        # Bob signs out. Upon doing this, he is redirected back to 'Kittens'
        # page.
        response = new_page.click(linkid='logout-link').follow()
        self.assertTitleEqual(response, u'MyWiki — Kittens')