# coding=utf-8
from base import BaseTestCase


class EditPageLayoutTest(BaseTestCase):
    def test_edit_page_renders_correctly(self):
        # Bob signs up and then opens edit page for MyWiki's homepage.
        self.sign_up()
        homepage = self.testapp.get('/')
        edit_page = homepage.click(linkid='edit-article-link')

        # Browser successfully delivers him edit page.
        self.assertEqual(edit_page.status_int, 200)

        # Page has an indicative title.
        self.assertTitleEqual(edit_page, u'MyWiki — Welcome to MyWiki! (edit)')

        # There's a form on page.
        self.assertIn('wiki-edit-form', edit_page.forms)

        # This form has a text input for title, text area for body and a submit
        # button.
        form_html = edit_page.pyquery('#wiki-edit-form')
        input_ = form_html.find('input#wiki-head')
        textarea = form_html.find('textarea#wiki-body')
        submit = form_html.find('input[type=submit]')
        self.assertTrue(all([input_, textarea, submit]))

        # Text input and text area already contain corresponding parts of the
        # homepage ready for editing.
        self.assertEqual(input_.attr('value'), 'Welcome to MyWiki!')
        self.assertEqual(
            textarea.text(),
            '<p>You are free to create new articles and edit existing '
            'ones.</p>')

    def test_edit_link_is_not_displayed_in_edit_page(self):
        # Bob signs up and then opens edit page for MyWiki's homepage.
        self.sign_up()
        response = self.testapp.get('/_edit/')

        # There is no "Edit Article" link in navigation panel.
        self.assertRaises(
            AssertionError, self.assertHasLink, response, '#edit-article-link')

    def test_has_link_to_homepage(self):
        # Bob signs up and the opens edit page for MyWiki's homepage.
        self.sign_up()
        response = self.testapp.get('/_edit/')

        # There's a link to homepage in navigation panel.
        self.assertHasLinkToHomepage(response)


class EditPageBehaviourTest(BaseTestCase):
    def test_unauthorized_user_is_redirected_to_login_page(self):
        # Bob tries to access edit page for MyWiki's homepage by direct link.
        # He's not logged in.
        response = self.testapp.get('/_edit/').follow()

        # Browser delivers him a login page.
        self.assertTitleEqual(response, 'MyWiki *** Login')

    def test_unauthorized_user_cannot_post_directly(self):
        # Bob tries to send a direct POST request to edit page for MyWiki's
        # homepage. He's not logged in.
        response = self.testapp.post('/_edit/').follow()

        # Browser delivers him a login page.
        self.assertTitleEqual(response, 'MyWiki *** Login')

    def test_redirects_back_to_edit_page_after_successful_login(self):
        # Bob signs up and immediately logs out.
        self.sign_up()
        self.testapp.get('/logout')

        # Then he tries to access edit page for MyWiki's homepage by direct
        # link.
        response = self.testapp.get('/_edit/').follow()

        # He is redirected to the login page, where On signs in as a newly
        # created user.
        login_response = self.fill_form(
            response, username='bob', password='test123').submit().follow()

        # Bob is redirected back to the edit page.
        self.assertTitleEqual(
            login_response, u'MyWiki — Welcome to MyWiki! (edit)')

        # He can even see his name in navigation panel.
        username_container = login_response.pyquery('#username')
        self.assertEqual(len(username_container), 1)
        self.assertEqual(username_container.text(), 'bob')

    def test_redirects_back_to_edit_page_after_successful_signup(self):
        # Bob tries to access edit page for MyWiki's homepage by direct link.
        response = self.testapp.get('/_edit/').follow()

        # He is redirected to the login page. Bob does not sign in -- he's not
        # registered and instead opts for signup page.
        signup_page = response.click(linkid='auth-alternative')

        # Signup page opens up. Bob signs up as a new user.
        signup_form = self.fill_form(
            signup_page, username='bob', password='test123', verify='test123')
        signup_response = signup_form.submit().follow()

        # He is redirected back to edit page for MyWiki's homepage.
        self.assertTitleEqual(
            signup_response, u'MyWiki — Welcome to MyWiki! (edit)')

    def test_logging_out_on_edit_page_redirects_to_corresponding_article(self):
        # Bob signs up and immediately creates a new article.
        new_article = self.create_article(
            '/kittens', body="Kittens are cute and cuddly.")

        # Bob clicks "Edit Article" link to introduce more changes into page,
        # but changes his mind and on edit page, which was delivered by
        # browser, he clicks "Sign Out".
        edit_page = new_article.click(linkid='edit-article-link')
        response = edit_page.click(linkid='logout-link').follow()

        # He's redirected to the article he was about to edit.
        self.assertTitleEqual(response, u'MyWiki — Kittens')

    def test_edit_page_has_link_to_history_in_edit_article_mode(self):
        # Bob signs up and immediately creates a new article.
        new_article = self.create_article('/elephants')

        # He clicks "Edit Article" link to open edit page for the newly created
        # article.
        edit_page = new_article.click(linkid='edit-article-link')

        # He notices a link to history on this page.
        history_link = edit_page.pyquery('a#history-link')
        self.assertTrue(bool(history_link))

    def test_edit_page_does_not_have_link_to_history_in_new_article_mode(self):
        # Bob signs up and immediately opens an edit page to create a new
        # article.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/sequoia')

        # He notices, that this page does not have a history link.
        history_link = edit_page.pyquery('a#history-link')
        self.assertFalse(bool(history_link))


class NewArticleTest(BaseTestCase):
    def test_requesting_nonexistent_article_opens_edit_page(self):
        # Bob signs up and tries to request an article, that doesn't exist yet.
        self.sign_up()
        response = self.testapp.get('/i_do_not_exist').follow()

        # The edit page opens up.
        self.assertTitleEqual(response, 'MyWiki *** New Article')

    # nea = non-existent article
    def test_requesting_history_of_nea_by_authorized_user_opens_edit_page(self):
        # Bob sings up and tries to request history of an article, that doesn't
        # exist yet.
        self.sign_up()
        response = self.testapp.get('/_history/i_never_existed').follow()

        # The edit page opens up.
        self.assertTitleEqual(response, 'MyWiki *** New Article')

        # It has a pre-filled "head" field, whose content is formed from
        # requested article's url.
        head_field = response.form['head']
        self.assertEqual(head_field.value, 'I Never Existed')

    def test_edit_page_makes_up_a_title_from_path(self):
        # Bob signs up and tries to request an article, that doesn't exist yet.
        self.sign_up()
        response = self.testapp.get('/kittens').follow()

        # The edit page opens up. Bob notices, that there's a word 'Kittens' in
        # upper input box -- exactly the word from the path he requested, only
        # capitalized.
        input_box_content = response.pyquery('#wiki-head').attr('value')
        self.assertEqual(input_box_content, 'Kittens')

        # He also notices the generic page title: New Article.
        self.assertTitleEqual(response, 'MyWiki *** New Article')

    def test_edit_page_correctly_handles_underscores_in_path(self):
        # Bob signs up and tries to request an article, that doesn't exist yet.
        # This time path to article contains underscores, that serve as word
        # delimiters.
        self.sign_up()
        response = self.testapp.get('/i_do_not_exist').follow()

        # The edit page opens up. Bob finds out, that requested path is rendered
        # into a text for article's title input box -- it is now a correct
        # fraze, where words are delimited by spaces and each one is
        # capitalized.
        input_box_content = response.pyquery('#wiki-head').attr('value')
        self.assertEqual(input_box_content, 'I Do Not Exist')

        # He also notices the generic page title: New Article.
        self.assertTitleEqual(response, 'MyWiki *** New Article')

    def test_new_article_can_be_saved_and_be_accessible_by_the_path(self):
        # Bob signs up and tries to request an article, that doesn't exist yet.
        self.sign_up()
        edit_page = self.testapp.get('/i_do_not_exist').follow()

        # In the edit page, Bob enters some text into textarea -- field for page
        # body -- and submit the form.
        edit_page_response = self.fill_form(
            edit_page, body='<p>This is some testing text.</p>').submit()
        edit_page_response = edit_page_response.follow()

        # He is redirected to the newly created article. This article has the
        # corresponding title.
        self.assertTitleEqual(edit_page_response, u'MyWiki — I Do Not Exist')

        # It has a corresponding head and body, that Bob edited on form.
        head = edit_page_response.pyquery('#wiki-head')
        body = edit_page_response.pyquery('#wiki-body')
        self.assertEqual(head.text(), 'I Do Not Exist')
        self.assertEqual(body.text(), 'This is some testing text.')

        # Bob logs out. And requests this article again.
        self.testapp.get('/logout')
        response = self.testapp.get('/i_do_not_exist')

        # Everything is still in place.
        self.assertTitleEqual(response, u'MyWiki — I Do Not Exist')
        head = edit_page_response.pyquery('#wiki-head')
        body = edit_page_response.pyquery('#wiki-body')
        self.assertEqual(head.text(), 'I Do Not Exist')
        self.assertEqual(body.text(), 'This is some testing text.')

    def test_can_edit_article_once_it_has_been_created(self):
        # Bob signs up and creates a new article right away.
        self.sign_up()
        edit_page = self.testapp.get('/kittens').follow()

        # Bob enters some data into form and saves the new article.
        self.fill_form(
            edit_page, head='Puppies',
            body='<p>Puppies are cute and cuddly</p>').submit()

        # He requests the newly created article.
        puppies_article = self.testapp.get('/kittens')

        # Bob clicks "Edit Article" link to access edit page for this article.
        edit_page = puppies_article.click(linkid='edit-article-link')

        # Edit page is successfully delivered to him.
        self.assertTitleEqual(edit_page, u'MyWiki — Puppies (edit)')

        # He slightly modifies article title and replaces the body. The he saves
        # the article once again.
        response = self.fill_form(
            edit_page, head='Suicidal Puppies',
            body="<h2>Banned by Roskomnadzor</h2>").submit().follow()

        # He can see, that the changes were applied successfully.
        self.assertTitleEqual(response, u'MyWiki — Suicidal Puppies')
        head = response.pyquery('#wiki-head')
        body = response.pyquery('#wiki-body')
        self.assertEqual(head.text(), 'Suicidal Puppies')
        self.assertEqual(body.text(), 'Banned by Roskomnadzor')

    def test_logging_out_while_creating_new_article_redirects_home(self):
        # Bob signs up and immediately opens an edit page for the new article.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/kittens')

        # On second thought, he decides not to create a new article, and logs 
        # out.
        response = edit_page.click(linkid='logout-link').follow()

        # He is redirected to homepage.
        self.assertTitleEqual(response, u'MyWiki — Welcome to MyWiki!')


class EditPageValidationTest(BaseTestCase):
    def test_article_title_cannot_be_empty(self):
        # Bob signs up and goes straight to edit page for MyWiki's homepage.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/')

        # He cleans the title and tries to save the article like this.
        response = self.fill_form(edit_page, head='').submit()

        # Page refreshes and he can see an error, complaining about empty title.
        self.assertTitleEqual(response, u'MyWiki — Welcome to MyWiki! (edit)')
        self.assertHasFormError(response, 'Head cannot be empty!')

        # However, article's title input box is left empty for Bob to correct
        # as he wills.
        input_box_content = response.pyquery('#wiki-head').attr('value')
        self.assertEqual(input_box_content, '')

    def test_article_can_be_saved_with_empty_body(self):
        # Bob signs up and creates a new article right away.
        self.sign_up()
        edit_page = self.testapp.get('/kittens').follow()

        # He cleans the body and tries to save the article like this.
        response = self.fill_form(edit_page, body='').submit().follow()

        # It is saved! Newly created article is served by browser.
        self.assertTitleEqual(response, u'MyWiki — Kittens')

        # It has a head, but has no body.
        head = response.pyquery('#wiki-head')
        body = response.pyquery('#wiki-body')
        self.assertEqual(head.text(), 'Kittens')
        self.assertEqual(body.text(), '')

    def test_article_head_cannot_exceed_256_characters(self):
        # Bob signs up and goes straight to edit page for MyWiki's homepage.
        self.sign_up()
        edit_page = self.testapp.get('/_edit/')

        # He attempts to give the article a head longer than 256 characters.
        overly_long_head = (
            'This is an absurdly long MyWiki article head crafted exclusively '
            'to test application\'s tolerance to verbose article heads, '
            'exceeding 256 characters in length. It is not that heads of such '
            'length will actually be used by somebody, it\'s about the need '
            'for the extreme point, which would hopefully result in cutting '
            'on entropy of the app.')
        edit_response = self.fill_form(
            edit_page, head=overly_long_head, body='Test body').submit()

        # Page refreshes and Bob sees an error message, complaining about the
        # length of the head.
        self.assertHasFormError(
            edit_response,
            'Article head is too long! Must not exceed 256 characters')

        # Everything Bob entered into the form is left intact.
        form = edit_response.form
        self.assertEqual(form['head'].value, overly_long_head)
        self.assertEqual(form['body'].value, 'Test body')


class VersionEditTest(BaseTestCase):
    def test_can_open_edit_page_for_version_by_direct_url(self):
        # Bob signs up and creates a new article.
        self.create_article('/mindfulness')

        # He edits it several times to make more versions.
        self.edit_article('/mindfulness', body='<p>Open your mind.</p>')
        self.edit_article('/mindfulness', body='<div>Express yourself.</div>')
        self.edit_article('/mindfulness', head='Insight')

        version_ids = self.fetch_version_ids('/mindfulness')

        # Bob opens the edit page for the first version by direct url. It
        # renders correctly.
        fv_edit_page = self.testapp.get(
            '/_edit/mindfulness/_version/{}'.format(version_ids[0]))
        self.assertIn('wiki-edit-form', fv_edit_page.forms)

        form = fv_edit_page.form
        self.assertEqual(form['head'].value, 'Mindfulness')
        self.assertEqual(form['body'].value, '')

        # Bob opens the edit page for the last version by direct url. It also
        # renders correctly.
        lv_edit_page = self.testapp.get(
            '/_edit/mindfulness/_version/{}'.format(version_ids[-1]))
        self.assertIn('wiki-edit-form', lv_edit_page.forms)

        form = lv_edit_page.form
        self.assertEqual(form['head'].value, 'Insight')
        self.assertEqual(form['body'].value, '<div>Express yourself.</div>')

        # Bob opens the edit page for the second version by direct url. It
        # renders correctly as well.
        edit_page = self.testapp.get(
            '/_edit/mindfulness/_version/{}'.format(version_ids[1]))
        self.assertIn('wiki-edit-form', edit_page.forms)

        form = edit_page.form
        self.assertEqual(form['head'].value, 'Mindfulness')
        self.assertEqual(form['body'].value, '<p>Open your mind.</p>')

    def test_saving_edited_version_creates_new_version(self):
        # Bob signs up and creates a new article.
        self.create_article('/future')

        # He edits it several times to create more versions.
        self.edit_article('/future', head='Not Past')
        self.edit_article('/future', body='<div>It awaits!</div>')

        version_ids = self.fetch_version_ids('/future')

        # Bob opens edit page for the second version of the article using
        # direct url.
        fv_edit_page = self.testapp.get(
            '/_edit/future/_version/{}'.format(version_ids[1]))

        # He changes body and saves the article.
        self.fill_form(
            fv_edit_page, body='<p>Do not be cruel to me.</p>').submit()

        # Bob opens article. Latest version is served by the browser. Bob can
        # see, that it reflects changes, which he introduced to the second
        # version.
        article = self.testapp.get('/future')
        head = article.pyquery('#wiki-head')
        body = article.pyquery('#wiki-body')
        self.assertEqual(head.text(), 'Not Past')
        self.assertEqual(body.text(), 'Do not be cruel to me.')

        label = article.pyquery('.distinction-label')
        self.assertTrue(bool(label))
        self.assertEqual(label.text(), '(current)')

    def test_old_version_is_not_changed_when_it_is_edited(self):
        # Bob signs up and creates a new article.
        self.create_article('/earth', body='<p>Our home.</p>')

        # He edits the article, to create one more version.
        self.edit_article('/earth', head='Solar System')

        version_ids = self.fetch_version_ids('/earth')

        # Bob opens the first version of the article for editing by direct url.
        fv_edit_page = self.testapp.get(
            '/_edit/earth/_version/{}'.format(version_ids[0]))

        # Bob introduces some changes and saves them.
        self.fill_form(
            fv_edit_page, head='Universe',
            body='<div>Our playground</div>').submit()

        # He opens the view page for the first version of the article. As he can
        # see, it hasn't changed.
        first_version = self.testapp.get(
            '/earth/_version/{}'.format(version_ids[0]))
        head = first_version.pyquery('#wiki-head')
        body = first_version.pyquery('#wiki-body')
        self.assertEqual(head.text(), 'Earth')
        self.assertEqual(body.text(), 'Our home.')

    def test_clicking_edit_on_version_view_page_edits_this_version(self):
        # /Bob signs up and creates a new article. He edits it once to add a new
        # version.
        self.create_article('/moon', body='<div>Goddess of mystery.</div>')
        self.edit_article('/moon', head='Selena', body='')

        version_ids = self.fetch_version_ids('/moon')

        # Bob opens the view page for the first version of the article. There he
        # clicks "Edit Article" link.
        first_version = self.testapp.get(
            '/moon/_version/{}'.format(version_ids[0]))
        response = first_version.click(linkid='edit-article-link')

        # The first version of the article is opened for editing.
        form = response.form
        self.assertEqual(form['head'].value, 'Moon')
        self.assertEqual(form['body'].value, '<div>Goddess of mystery.</div>')