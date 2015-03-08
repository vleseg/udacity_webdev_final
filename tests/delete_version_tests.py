from base import BaseTestCase
# Internal project imports.
from model import Article


class BasicDeleteVersionTest(BaseTestCase):
    def test_delete_handler_is_accessible_by_direct_url(self):
        # Bob sings up and creates a new article. He modifies the article to
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
        # Bob sings up and creates a new article. He modifies it several times
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

    # TODO: find and replace "def tets_*" with "def test_*"
    def test_when_latest_version_is_deleted_shift_pointer(self):
        # Bob sings up and creates an article. He modifies it several times
        # to add more versions.
        self.create_article('/test_shifting_pointer')
        self.edit_article(
            '/test_shifting_pointer', title="Test Deleting Latest Version")
        self.edit_article('/test_shifting_pointer')

        ver_ids = self.fetch_version_ids('/test_shifting_pointer')

        # Bob deletes latest version of the article by triggering the delete
        # handler.
        self.testapp.get(
            '/_delete/test_shifting_pointer/_version/{}'.format(ver_ids[-1]))

        # Former second (middle) version becomes the latest.
        latest_version = Article.by_url('/test_shifting_pointer').latest_version
        self.assertEqual(latest_version.id, ver_ids[1])