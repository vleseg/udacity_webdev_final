# coding=utf-8
from base import BaseTestCase


class BasicHomepageTest(BaseTestCase):
    def test_home_page_opens_and_displays_correct_content(self):
        # Bob types in MyWiki's home page address and presses Return. Browser
        # successfully delivers him the home page.
        homepage = self.testapp.get('/')
        self.assertEqual(homepage.status_int, 200)
        self.assertTitleEqual(homepage, u'MyWiki — Welcome to MyWiki!')

        # Bob finds a heading followed by a piece of text, that both give him
        # an idea, that he really is on MyWiki's homepage.
        content = homepage.pyquery('#wiki-content')
        heading = content.find('#wiki-heading')
        body = content.find('#wiki-body')
        self.assertEqual(heading.text(), 'Welcome to MyWiki!')
        self.assertEqual(
            body.text(),
            'You are free to create new pages and edit existing ones.')

    def test_homepage_panel_displays_correct_things_to_unauthorized_user(self):
        # Bob opens MyWiki's homepage.
        homepage = self.testapp.get('/')

        # There's a navigation panel at the top of the page.
        top_panel = homepage.pyquery('#top-panel')
        self.assertEqual(len(top_panel), 1)

        # Navigation panel has "Sign In" and "Sign Up" links. They point at,
        # correspondingly, login page and signup page.
        links = top_panel.find('a')
        links_dict = dict((link.text, link.get('href')) for link in links)
        self.assertDictContainsSubset(
            {'Sign Up': '/signup', 'Sign In': '/login'}, links_dict)

    def test_homepage_panel_displays_correct_things_to_authorized_user(self):
        # Bob sings up for MyWiki
        self.sign_up()

        # Then he opens MyWiki's homepage.
        homepage = self.testapp.get('/')

        # There's a navigation panel at the top of the page.
        top_panel = homepage.pyquery('#top-panel')
        self.assertEqual(len(top_panel), 1)

        # Navigation panel has Bob's name in it.
        self.assertIn('bob', top_panel.text())

        # It also contains two links:
        # "Edit Page", leading to page editing form, and "Sign Out", that
        # triggers signout handler.
        links = top_panel.find('a')
        links_dict = dict((link.text, link.get('href')) for link in links)
        self.assertDictContainsSubset(
            {'Sign Out': '/logout', 'Edit Page': '/_edit/'}, links_dict)