"""Tests for the flask code."""

from unittest import TestCase

# be able to import from parent dir
import sys
sys.path.append('..')

from server import app


class FlaskTests(TestCase):
    """Test Flask functionality."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def tearDown(self):
      """Stuff to do after each test."""


