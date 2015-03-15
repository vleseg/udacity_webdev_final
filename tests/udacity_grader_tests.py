from base import BaseTestCase


class UdacityGraderBaseTest(BaseTestCase):
    def test_basic_workflow(self):
        self.sign_up(username='bob', password='test', verify='test')
        edit_page = self.testapp.get('/blaRGH')
        self.assertEqual(edit_page.status_int, 302)
        post_params = {
            'content': 'vPcYImdjOXfZhIZtBnYnRgrGsJLMyFlTbvbIPwZawUcGLnlPODRocQQLOWxI'}
        new_article = self.testapp.post('/_edit/blaRGH', params=post_params)
        self.assertEqual(edit_page.status_int, 302)