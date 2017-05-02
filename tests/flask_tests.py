"""Tests for the flask code."""

    # Copyright (c) 2017 Bonnie Schulkin

    # This file is part of My Heavens.

    # My Heavens is free software: you can redistribute it and/or modify it under
    # the terms of the GNU Affero General Public License as published by the Free
    # Software Foundation, either version 3 of the License, or (at your option)
    # any later version.

    # My Heavens is distributed in the hope that it will be useful, but WITHOUT
    # ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    # FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
    # for more details.

    # You should have received a copy of the GNU Affero General Public License
    # along with My Heavens. If not, see <http://www.gnu.org/licenses/>.

from unittest import TestCase
import json

# be able to import from parent dir
import sys
sys.path.append('..')

from server import app
from run_tests import DbTestCase

# for posting to stars.json
TEST_DATETIME_STRING = '2017-03-01T21:00'


class FlaskHTMLTests(TestCase):
    """Test Flask functionality for returned HTML."""

    def setUp(self):
        """Stuff to do before every test."""

        client = app.test_client()
        app.config['TESTING'] = True
        self.response = client.get('/')

    def test_status(self):
        """Make sure the status is 200."""

        self.assertEqual(self.response.status_code, 200)

    def test_title(self):
        """Test main page load."""

        self.assertIn('<title>My Heavens</title>', self.response.data)

    def test_home_tab(self):
        """Test that the home tab exists."""

        self.assertIn('div id=\'home\'', self.response.data)

    def test_stars_tab(self):
        """Test that the stars tab exists."""

        self.assertIn('div id=\'star-map\'', self.response.data)

    def test_glossary_tab(self):
        """Test that the glossary tab exists."""

        self.assertIn('div id=\'glossary\'', self.response.data)

    def test_about_tab(self):
        """Test that the about tab exists."""

        self.assertIn('div id=\'about\'', self.response.data)

class FlaskDefinitionTests(TestCase):
    """Flask tests that aren't testing html, and don't require the db."""

    @classmethod
    def setUpClass(cls):
        """Stuff to do before every test."""

        client = app.test_client()
        app.config['TESTING'] = True
        cls.response = client.get('/terms.json')
        json_dict = json.loads(cls.response.data)
        cls.example_term, cls.example_def = json_dict.popitem()

    def test_status(self):
        """Make sure the status is 200."""

        self.assertEqual(self.response.status_code, 200)

    def test_datatype(self):
        """Test that response is json."""

        self.assertEqual(self.response.content_type, 'application/json')

    def test_key_datatype(self):
        """Test that the key of the example item is a unicode string."""

        self.assertIsInstance(self.example_term, unicode)

    def test_value_wiki_key(self):
        """Test that 'wikipedia' is one of the keys of the example item.

        Note: 'term' may or may not be a key, so must test others independently
        """

        self.assertIn('wikipedia', set(self.example_def.keys()))

    def test_value_def_key(self):
        """Test that 'definition' is one of the keys of the example item.

        Note: 'term' may or may not be a key, so must test others independently
        """

        self.assertIn('definition', set(self.example_def.keys()))


class FlaskStarDataTests(DbTestCase):
    """Test Flask star data json route.

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(FlaskStarDataTests, cls).setUpClass()
        super(FlaskStarDataTests, cls).load_test_data()

        client = app.test_client()
        app.config['TESTING'] = True

        cls.response = client.get('/stars.json')
        cls.json_dict = json.loads(cls.response.data)

    def test_status(self):
        """Make sure the status is 200."""

        self.assertEqual(self.response.status_code, 200)

    def test_datatype(self):
        """Test that response is json."""

        self.assertEqual(self.response.content_type, 'application/json')

    def test_value_keys(self):
        """Test the value keys of the example item."""

        self.assertEqual(set(self.json_dict.keys()), 
                         set(['constellations', 'stars']))


class FlaskPlacetimeDataTests(DbTestCase):
    """Test Flask place / time data json route.

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(FlaskPlacetimeDataTests, cls).setUpClass()
        super(FlaskPlacetimeDataTests, cls).load_test_data()

        client = app.test_client()
        app.config['TESTING'] = True

        data = {'lat': 0, 'lng': 0}
        cls.response = client.post('/place-time-data.json', data=data)
        cls.json_dict = json.loads(cls.response.data)

    def test_status(self):
        """Make sure the status is 200."""

        self.assertEqual(self.response.status_code, 200)

    def test_datatype(self):
        """Test that response is json."""

        self.assertEqual(self.response.content_type, 'application/json')

    def test_value_keys(self):
        """Test the value keys of the example item."""

        self.assertEqual(set(self.json_dict.keys()), 
                    set(['dateloc', 'rotation', 'planets', 'sundata', 'moon']))

