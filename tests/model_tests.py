from datetime import datetime, timedelta
from time import sleep
# Internal project imports
from base import BaseTestCase
from model import Article


class ArticleVersionTest(BaseTestCase):
    def test_version_timestamp_stores_a_correct_value(self):
        self.create_article('/kittens')
        t = datetime.utcnow()

        version_ts = Article.by_url('/kittens').modified
        self.assertAlmostEqual(t, version_ts, delta=timedelta(1))

    def test_version_ids_are_sequential(self):
        a = Article.new('/jazz', 'Jazz', '')
        sleep(0.1)
        a.new_version('Jazz', 'Pass me the jazz')
        sleep(0.1)
        a.new_version('Buzz', 'Biz')
        sleep(0.1)
        v_list = list(a.version_set)

        version_by_created = sorted(v_list, key=lambda v: v.created)
        version_by_id = sorted(v_list, key=lambda v: v.key().id())
        self.assertListEqual(version_by_created, version_by_id)

    def test_first_and_latest_version_pointers_are_stored_correctly(self):
        a = Article.new('/test', 'Test', '')
        self.assertEqual(a.first_version().head, 'Test')
        self.assertEqual(a.first_version().body, '')
        self.assertEqual(a.latest_version().head, 'Test')
        self.assertEqual(a.latest_version().body, '')

        a.new_version('Testing', 'abc')
        self.assertEqual(a.latest_version().head, 'Testing')
        self.assertEqual(a.latest_version().body, 'abc')

        a.new_version('The End', 'xyz')
        self.assertEqual(a.latest_version().head, 'The End')
        self.assertEqual(a.latest_version().body, 'xyz')
        self.assertEqual(a.first_version().head, 'Test')
        self.assertEqual(a.first_version().body, '')