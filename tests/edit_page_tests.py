# coding=utf-8
from base import BaseTestCase


class BasicEditPageTest(BaseTestCase):
    def test_edit_form_renders_correctly(self):
        # Bob signs up and then opens edit form for MyWiki's homepage.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/')

        # Browser successfully delivers him edit form.
        self.assertEqual(edit_page.status_int, 200)

        # Page has an indicative title.
        self.assertTitleEqual(edit_page, u'MyWiki — Welcome to MyWiki! (edit)')

        # There's a form on page.
        self.assertIn('wiki-edit-form', edit_page.forms)

        # This form has a text input for title, text area for body and a submit
        # button.
        form_html = edit_page.pyquery('#wiki-edit-form')
        input_ = form_html.find('input#wiki-title')
        textarea = form_html.find('textarea#wiki-body')
        submit = form_html.find('input[type=submit]')
        self.assertTrue(all([input_, textarea, submit]))

        # Text input and text area already contain corresponding parts of the
        # home page ready for editing.
        self.assertEqual(input_.attr('value'), 'Welcome to MyWiki!')
        self.assertEqual(
            textarea.text(),
            '<p>You are free to create new pages and edit existing ones.</p>')

    def test_unauthorized_user_is_redirected_to_login_page(self):
        # Bob tries to access edit form for MyWiki's home page by direct link.
        # He's not logged in.
        response = self.testapp.get('/_edit/').follow()

        # Browser delivers him a login page.
        self.assertTitleEqual(response, u'MyWiki — Login')

    def test_redirects_back_to_edit_form_after_successful_login(self):
        # Bob signs up and immediately logs off.
        self.sign_up()
        self.testapp.get('/logout')

        # Then he tries to access edit form for MyWiki's home page by direct
        # link.
        response = self.testapp.get('/_edit/').follow()

        # On the login form he signs in as a newly created user.
        login_response = self.fill_form(
            response, username='bob', password='test123').submit().follow()

        # Bob is redirected back to the edit form.
        self.assertTitleEqual(
            login_response, u'MyWiki — Welcome to MyWiki! (edit)')

        # He can even see his name in navigation panel.
        username_container = login_response.pyquery('#username')
        self.assertEqual(len(username_container), 1)
        self.assertEqual(username_container.text(), 'bob')