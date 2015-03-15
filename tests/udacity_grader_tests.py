from base import BaseTestCase


class UdacityGraderBaseTest(BaseTestCase):
    def test_basic_workflow(self):
        self.sign_up(username='bob', password='test', verify='test')
        edit_page = self.testapp.get('/blaRGH')
        self.assertEqual(edit_page.status_int, 302)
        post_params = {
            'content': 'vPcYImdjOXfZnRgrGsJLMyFlTbvbIPwZawUcGLnlPODRocQQLOWxI'}
        new_article = self.testapp.post(
            '/_edit/blaRGH', params=post_params).follow()
        self.assertEqual(new_article.status_int, 200)
        self.assertIn(
            'vPcYImdjOXfZnRgrGsJLMyFlTbvbIPwZawUcGLnlPODRocQQLOWxI',
            new_article)
        history_page = new_article.click(linkid='history-link')
        self.assertEqual(history_page.status_int, 200)
        self.assertIn(
            'vPcYImdjOXfZnRgrGsJLMyFlTbvbIPwZawUcGLnlPODRocQQLOWxI',
            history_page)