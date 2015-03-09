# coding=utf-8
from base import BaseTestCase


class BasicDeleteVersionTest(BaseTestCase):
    def test_delete_handler_is_accessible_by_direct_url(self):
        # Bob signs up and creates a new article. He modifies the article to
        # create a new version.
        self.create_article('/delete_my_version')
        self.edit_article(
            '/delete_my_version', body='<p>..and do it quickly!</p>')

        version_ids = self.fetch_version_ids('/delete_my_version')

        # He tries to access the delete handler for both versions of the page
        # consecutively. The handler is accessible.
        response_1 = self.testapp.get(
            '/_delete/delete_my_version/_version/{}'.format(version_ids[0]))
        response_2 = self.testapp.get(
            '/_delete/delete_my_version/_version/{}'.format(version_ids[1]))

        self.assertNotEqual(response_1.status_int, 404)
        self.assertNotEqual(response_2.status_int, 404)

    def test_touching_delete_handler_deletes_corresponding_version(self):
        # Bob signs up and creates a new article. He modifies it several times
        # to create more versions.
        self.create_article('/test_deleting')
        self.edit_article(
            '/test_deleting', body='<p>This version will be deleted.</p>')
        self.edit_article(
            '/test_deleting', body='<p>This one will stay..</p>')
        self.edit_article(
            '/test_deleting', body='<p>This must go away too..</p>')

        version_ids = self.fetch_version_ids('/test_deleting')

        # Bob triggers the delete handler against two versions of the article.
        to_delete_id_1 = version_ids[1]
        to_delete_id_2 = version_ids[3]
        self.testapp.get(
            '/_delete/test_deleting/_version/{}'.format(to_delete_id_1))
        self.testapp.get(
            '/_delete/test_deleting/_version/{}'.format(to_delete_id_2))

        # Deleted versions are actually gone.
        version_ids = self.fetch_version_ids('/test_deleting')
        self.assertNotIn(to_delete_id_1, version_ids)
        self.assertNotIn(to_delete_id_2, version_ids)

    def test_only_authorized_users_can_delete_versions(self):
        # Bob signs up and creates a new article. He modifies it once to create
        # a new version.
        self.create_article('/test_auth_delete')
        self.edit_article(
            '/test_auth_delete', body='<p>Will not be able to delete.</p>')

        # Bob sings out.
        self.testapp.get('/logout')

        fv_id = self.fetch_version_ids('/test_auth_delete')[0]

        # He tries to access delete handler to delete the first version of the
        # article.
        self.testapp.get('/_delete/test_auth_delete/_version/{}'.format(fv_id))

        # Version is not deleted.
        self.assertEqual(len(self.fetch_version_ids('/test_auth_delete')), 2)

    def test_redirect_to_latest_version_after_deleting(self):
        # Bob signs up and creates an article. He modifies it several times to
        # create more versions.
        self.create_article('/test_redirecting')
        self.edit_article('/test_redirecting', head='Must Redirect')
        self.edit_article('/test_redirecting', head='Will Redirect')
        self.edit_article('/test_redirecting', body='<p>In any case.</p>')

        version_ids = self.fetch_version_ids('/test_redirecting')

        # Bob deletes the second version via delete handler. Handler redirects
        # him to the latest version.
        response = self.testapp.get(
            '/_delete/test_redirecting/_version/{}'.format(
                version_ids[1])).follow()
        self.assertTitleEqual(response, u'MyWiki — Will Redirect')
        self.assertEqual(response.pyquery('#wiki-head').text(), 'Will Redirect')
        self.assertEqual(response.pyquery('#wiki-body').text(), 'In any case.')

        # After that Bob deletes the latest version via delete handler. Handler
        # redirects him to the former third version, which has now become the
        # latest.
        response = self.testapp.get(
            '/_delete/test_redirecting/_version/{}'.format(
                version_ids[-1])).follow()
        self.assertTitleEqual(response, u'MyWiki — Will Redirect')
        self.assertEqual(response.pyquery('#wiki-head').text(), 'Will Redirect')
        self.assertEqual(response.pyquery('#wiki-body').text(), '')


class PointerTest(BaseTestCase):
    def test_when_latest_version_is_deleted_shift_pointer(self):
        # Bob signs up and creates an article. He modifies it several times
        # to add more versions.
        self.create_article('/test_shifting_pointer')
        self.edit_article(
            '/test_shifting_pointer', head="Test Deleting Latest Version")
        self.edit_article(
            '/test_shifting_pointer', body='<p>Pointer shifts backwards.</p>')

        ver_ids = self.fetch_version_ids('/test_shifting_pointer')

        # Bob deletes latest version of the article by triggering the delete
        # handler.
        self.testapp.get(
            '/_delete/test_shifting_pointer/_version/{}'.format(ver_ids[-1]))

        # Former second (middle) version becomes the latest.
        latest_version = self.article_model.by_url(
            '/test_shifting_pointer').latest_version
        self.assertEqual(latest_version.id, ver_ids[1])

    def test_when_first_version_is_deleted_shift_pointer(self):
        # Bob signs up and creates an article. He modifies it several times
        # to add more versions.
        self.create_article('/test_shifting_pointer')
        self.edit_article(
            '/test_shifting_pointer', head='Test Deleting First Version')
        self.edit_article(
            '/test_shifting_pointer', body='<p>Pointer shifts forwards.</p>')

        ver_ids = self.fetch_version_ids('/test_shifting_pointer')

        # Bob deletes first version of the article by triggering the delete
        # handler.
        self.testapp.get(
            '/_delete/test_shifting_pointer/_version/{}'.format(ver_ids[0]))

        # Former second (middle) version becomes the first.
        first_version = self.article_model.by_url(
            '/test_shifting_pointer').first_version
        self.assertEqual(first_version.id, ver_ids[1])