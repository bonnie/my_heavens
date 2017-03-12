"""Tests for the flask code."""

from unittest import TestCase
import json

# be able to import from parent dir
import sys
sys.path.append('..')

from server import app
from run_tests import DbTestCase

# for posting to stars.json
TEST_DATETIME_STRING = '2017-03-01T21:00'


class FlaskTests(TestCase):
    """Test Flask functionality."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_stars_page(self):
        """Test star chart display."""

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('<title>Star Charts</title>', response.data)


    # TODO: add lots more tests here

class FlaskTestsWithDb(DbTestCase):
    """Test Flask routes requiring db.

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(FlaskTestsWithDb, cls).setUpClass()
        super(FlaskTestsWithDb, cls).load_test_data()


    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True


    def test_star_data_json(self):
        """Test json returned for stars and constellations."""

        # lat, lng and datetime don't matter for this test
        data = {'lat': 0, 'lng': 0}

        response = self.client.post('/stars.json', data=data)
        json_dict = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(json_dict.keys()), 
                         set(['constellations', 'stars', 'planets', 'moon']))