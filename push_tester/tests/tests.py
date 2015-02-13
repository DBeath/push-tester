import unittest
from flask.ext.testing import TestCase
from push_tester import app, db
from push_tester.models import *


class MainTestCase(TestCase):

    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        app.config['TESTING'] = True
        app.config['DEBUG'] = True
        self.app = app.test_client()
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class FeedTests(MainTestCase):

    def test_ping(self):
        assert True

    # def test_feed_header(self):
    #     feed = Feed()

if __name__ == '__main__':
    unittest.main()
