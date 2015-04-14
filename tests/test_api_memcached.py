import unittest
from app.models import Memcached
from app import create_app, db


class MemcachedTestCase(unittest.TestCase):
    def setUp(self):
        #self.app = create_app('testing')
        self.app = create_app('default')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def test_get_by_host_and_port(self):
        root_path = '/api/v1.0/memcached/{host_type}/{ip}/port/{port}'
        rv = self.client.get(root_path.format(host_type="host", ip='10.57.66.123', port=11212))
        print rv.data
        self.assertEqual(rv.status_code, 200)

    def tearDown(self):
        self.app_context.pop()
