import unittest
from app.models import User


class UserModelTestCase(unittest.TestCase):
    PASSWORD1 = 'cat'
    PASSWORD2 = 'dog'

    def test_password_setter(self):
        u = User(password=self.PASSWORD1)
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password=self.PASSWORD1)
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password=self.PASSWORD1)
        self.assertTrue(u.verify_password(self.PASSWORD1))
        self.assertFalse(u.verify_password(self.PASSWORD2))

    def test_password_salt_are_random(self):
        u = User(password=self.PASSWORD1)
        u2 = User(password=self.PASSWORD1)
        self.assertTrue(u.password_hash != u2.password_hash)
