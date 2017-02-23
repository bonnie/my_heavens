"""tests for star charts app"""

from unittest import TestCase
from server import app
from model import connect_to_db, db


DATA_DIR = 'test_data'
TESTDB_URI = 'postgresql:///star_tests'


class SeedTests(unittest.TestCase):
  """Test the code to seed the database."""

    def SetUp():
    """Stuff to do before every test."""

    def TearDown():
    """Stuff to do after every test."""

    def test


class DbTests(unittest.TestCase):
    """Test retrieving data from the database."""


class CalculationTests(unittest.TestCase):  
    """Test calculations to retrieve star and constellation data."""


class FlaskTests(unittest.TestCase):
    """Test Flask functionality."""

    def setUp(self):
        # """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def tearDown(self):
      """Stuff to do after each test."""


if __name__ == '__main__':

  # run the tests
  unittest.main()
