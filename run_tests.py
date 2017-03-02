"""Tests for star charts app. 

This file simply collects and runs tests in other files (separated for better
organization). It also holds common constants."""

import unittest
from model import db, connect_to_db 
from server import app
from seed import load_seed_data


TESTDB_URI = 'postgresql:///star_tests'
TESTDATA_DIR = 'tests/test_data'


class DbTestCase(unittest.TestCase):
    """Parent class for tests that need db setup"""

    @classmethod
    def load_test_data(cls):
        """Load test data into db."""

        load_seed_data(TESTDATA_DIR)


    @classmethod
    def db_setup(cls):
        """Set up database for testing"""

        connect_to_db(app, TESTDB_URI)
        db.create_all()
        

    @classmethod
    def db_teardown(cls):
        """Tear down database for testing"""

        db.session.close()
        db.drop_all()


    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        cls.db_setup()


    @classmethod
    def tearDownClass(cls):
        """Stuff to do once after running all class test methods."""

        cls.db_teardown()
  

if __name__ == '__main__':

    # import the tests
    from tests.seed_tests import SeedTestsWithoutDb, SeedTestsWithDb, \
        SeedConstellationTests, SeedStarTests, SeedConstLineTests
    from tests.starfield_tests import StarFieldTestsWithoutDb, \
        StarFieldStarDataTests, StarFieldConstellationDataTests
    from tests.db_tests import DbTests
    from tests.flask_tests import FlaskTests

    # run the tests
    unittest.main()
