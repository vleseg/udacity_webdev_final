# coding=utf-8
from base import BaseTestCase


class BasicHomepageTest(BaseTestCase):
    def test_homepage_opens_and_displays_correct_content(self):
        # Bob types in MyWiki's homepage address and presses Return. Browser
        # successfully delivers him the homepage.
        homepage = self.testapp.get('/')
        self.assertEqual(homepage.status_int, 200)
        self.assertTitleEqual(homepage, u'MyWiki — Welcome to MyWiki!')

        # Bob finds a head followed by a piece of text, that both give him an
        # idea, that he really is on MyWiki's homepage.
        head = homepage.pyquery('#wiki-head')
        body = homepage.pyquery('#wiki-body')
        self.assertEqual(head.text(), 'Welcome to MyWiki!')
        self.assertEqual(
            body.text(),
            'You are free to create new articles and edit existing ones.')

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
        # "Edit Page", leading to article edit form, and "Sign Out", that
        # triggers signout handler.
        links = top_panel.find('a')
        links_dict = dict((link.text, link.get('href')) for link in links)
        self.assertDictContainsSubset(
            {'Sign Out': '/logout', 'Edit Article': '/_edit/'}, links_dict)
        
    def test_does_not_contain_link_to_self(self):
        # Bop opens the homepage.
        homepage = self.testapp.get('/')
        
        # He remembers that every article in MyWiki contains link to the
        # homepage. But it occurs that homepage itself does not. Which, on
        # second thought, is quite logical.
        self.assertRaises(
            AssertionError, self.assertHasLinkToHomepage, homepage)