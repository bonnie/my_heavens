"""Tests for the flask code."""

from unittest import TestCase
import json

# be able to import from parent dir
import sys
sys.path.append('..')

from server import app
from run_tests import DbTestCase


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

        response = self.client.get('/stars.json')
        json_dict = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(set(json_dict.keys()), 
                         set(['constellations', 'radius', 'stars']))