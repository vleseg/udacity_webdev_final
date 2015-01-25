# coding=utf-8
from base import BaseTestCase


class BasicEditPageTest(BaseTestCase):
    def test_edit_form_renders_correctly(self):
        # Bob signs up and then opens edit form for MyWiki's homepage.
        self.sign_up()
        homepage = self.testapp.get('/')
        edit_page = homepage.click(linkid='edit-page')

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
        # Bob signs up and immediately logs out.
        self.sign_up()
        self.testapp.get('/logout')

        # Then he tries to access edit form for MyWiki's home page by direct
        # link.
        response = self.testapp.get('/_edit/').follow()

        # He is redirected to the login page, where On signs in as a newly
        # created user.
        login_response = self.fill_form(
            response, username='bob', password='test123').submit().follow()

        # Bob is redirected back to the edit form.
        self.assertTitleEqual(
            login_response, u'MyWiki — Welcome to MyWiki! (edit)')

        # He can even see his name in navigation panel.
        username_container = login_response.pyquery('#username')
        self.assertEqual(len(username_container), 1)
        self.assertEqual(username_container.text(), 'bob')

    def test_redirects_back_to_edit_form_after_successful_signup(self):
        # Bob tries to access edit form for MyWiki's home page by direct link.
        response = self.testapp.get('/_edit/').follow()

        # He is redirected to the login page. Bob does not sign in -- he's not
        # registered and instead opts for signup page.
        signup_page = response.click(linkid='auth-alternative')

        # Signup page opens up. Bob signs up as a new user.
        signup_form = self.fill_form(
            signup_page, username='bob', password='test123', verify='test123')
        signup_response = signup_form.submit().follow()

        # He is redirected back to edit form for MyWiki's home page.
        self.assertTitleEqual(
            signup_response, u'MyWiki — Welcome to MyWiki! (edit)')
    #
    # def test_page_title_cannot_exceed_256_characters(self):
    #     # Bob signs up and goes straight to edit form for MyWiki's homepage.
    #     self.sign_up()
    #     edit_page = self.testapp.get('/_edit/')
    #
    #     # He attempts to give page a title longer than 256 characters.
    #     overly_long_title = (
    #         'This is an absurdly long MyWiki page title crafted exclusively to '
    #         'test application\'s tolerance to verbose page titles, exceeding '
    #         '256 characters in length. It is not that titles of such length '
    #         'will actually be used by somebody, it\'s about the need for the '
    #         'extreme point, which would hopefully result in cutting on '
    #         'entropy of the app.')
    #     edit_response = self.fill_form(
    #         edit_page, title=overly_long_title, body='Test body').submit()
    #
    #     # Page refreshes and Bob sees an error message, complaining about the
    #     # length of the title.
    #     self.assertHasFormError(
    #         edit_response,
    #         'Page title is too long! Must not exceed 256 characters')
    #
    #     # Everything Bob entered into the form is left intact.
    #     form = edit_response.form
    #     self.assertEqual(form['title'], overly_long_title)
    #     self.assertEqual(form['body'], 'Test body')