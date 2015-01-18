# coding=utf-8
from base import BaseTestCase


class BasicHomepageTest(BaseTestCase):
    def test_home_page_opens_and_displays_correct_content(self):
        # Bob types in MyWiki's home page address and presses Return. Browser
        # successfully delivers him the home page.
        homepage = self.testapp.get('/')
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