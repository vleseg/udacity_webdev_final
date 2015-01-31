from base import BaseTestCase


class BasicViewPageTest(BaseTestCase):
    def test_404_is_returned_when_nonexistent_page_is_requested(self):
        # Bob tries to fetch a page, that certainly does not exist.
        response = self.testapp.get('/i_do_not_exist', expect_errors=True)

        # He receives a 404 and a brief error text.
        self.assertTitleEqual(response, 'MyWiki *** Page not found')
        self.assertEqual(response.status_int, 404)
        self.assertEqual(
            response.pyquery('#error-message').text(), 'Page not found')

        # Top panel is present on the page too.
        self.assertEqual(len(response.pyquery('#top-panel')), 1)
        
        # There is also a link to the homepage.
        self.assertHasLinkToHomepage(response)

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