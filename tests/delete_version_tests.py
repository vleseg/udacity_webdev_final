# coding=utf-8
from random import randint
# Internal project imports
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
            '/_delete/delete_my_version/_version/{}'.format(version_ids[0]),
            expect_errors=True)
        response_2 = self.testapp.get(
            '/_delete/delete_my_version/_version/{}'.format(version_ids[1]),
            expect_errors=True)

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


class ErrorTest(BaseTestCase):
    def test_403_when_attempting_to_delete_the_only_version(self):
        # Bob signs up and creates a new article.
        self.create_article('/one_version')

        ver_id = self.fetch_version_ids('/one_version')[0]

        # Bob tries to delete article's sole version. Error 403 is returned
        # to him.
        response = self.testapp.get(
            '/_delete/one_version/_version/{}'.format(ver_id),
            expect_errors=True)
        self.assertEqual(response.status_int, 403)

    def test_do_not_delete_the_only_version(self):
        # Bob sings up and creates a new article.
        self.create_article(
            '/you_cant_delete_me', body='<div>Not worth trying.</div>')

        ver_id = self.fetch_version_ids('/you_cant_delete_me')[0]

        # Bob tries to delete article's sole version.
        self.testapp.get(
            '/_delete/you_cant_delete_me/_version/{}'.format(ver_id),
            expect_errors=True)

        # Version is not removed: Bob can request the article and its first
        # version will be returned.
        article = self.testapp.get('/you_cant_delete_me')
        self.assertTitleEqual(article, u'MyWiki — You Cant Delete Me')
        self.assertEqual(
            article.pyquery('#wiki-head').text(), 'You Cant Delete Me')
        self.assertEqual(
            article.pyquery('#wiki-body').text(), 'Not worth trying.')

    def test_404_when_trying_to_delete_nonexistent_version(self):
        # Bob signs up and creates an article.
        self.create_article('/delete_random')

        fake_version_id = self.get_fake_version_id('/delete_random')

        # Bob tries to delete version that certainly does not exist via direct
        # url
        response = self.testapp.get(
            '/_delete/delete_random/_version/{}'.format(fake_version_id),
            expect_errors=True)

        # He gets a 404.
        self.assertEqual(response.status_int, 404)

    def test_404_when_trying_to_delete_version_of_nonexistent_article(self):
        # Bob signs up and immediately checks if he can delete a nonexistent
        # version of a nonexistent article.
        self.sign_up()
        response = self.testapp.get(
            '/_delete/i_do_not_exist/_version/{}'.format(randint(0, 10)),
            expect_errors=True
        )

        # Of course he can't.
        self.assertEqual(response.status_int, 404)

    def test_404_if_article_and_version_are_not_related(self):
        # Bob signs up and creates two articles.
        self.create_article('/life')
        self.create_article('/death', sign_up=False)

        # He edits both articles to add a version to each.
        self.edit_article('/life', body='<p>Make most of out it.</p>')
        self.edit_article('/death', body='<p>Meet it with dignity.</p>')

        version_ids_1 = self.fetch_version_ids('/life')

        # Bob tries to delete a version which does not belong to the article
        # defined in url alongside with version id.
        response = self.testapp.get(
            '/_delete/death/_version/{}'.format(version_ids_1[0]),
            expect_errors=True)

        # A 404 page is returned to him.
        self.assertEqual(response.status_int, 404)

        # Versions in both articles are kept intact.
        version_ids_1 = self.fetch_version_ids('/life')
        version_ids_2 = self.fetch_version_ids('/death')

        self.assertEqual(len(version_ids_1), 2)
        self.assertEqual(len(version_ids_2), 2)

    def test_403_when_unauthorized_user_tries_to_delete_a_version(self):
        # Bob sings up and creates an article. He edits it to add a spare
        # version.
        self.create_article('/bugs')
        self.edit_article('/bugs', body='<div>A lot of them.</div>')

        version_ids = self.fetch_version_ids('/bugs')

        # Bob signs out and then tries to delete one of article's version via
        # direct url.
        self.testapp.get('/logout')
        response = self.testapp.get(
            '/_delete/bugs/_version/{}'.format(version_ids[0]),
            expect_errors=True)

        # A 403 error is delivered to him.
        self.assertEqual(response.status_int, 403)

        # Article's versions are not affected.
        version_ids = self.fetch_version_ids('/bugs')
        self.assertEqual(len(version_ids), 2)


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