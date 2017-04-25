"""Tests for my heavens app. 

This file simply collects and runs tests in other files (separated for better
organization). It also holds common constants."""

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

import unittest
from datetime import datetime

from model import db, connect_to_db 
from server import app
from seed import load_seed_data
from starfield import StarField, BOOTSTRAP_DTIME_FORMAT


TESTDB_URI = 'postgresql:///star_tests'
TESTDATA_DIR = 'tests/test_data'

# common starfields for starfield_tests.py and star_const_tests.py

MAX_MAG = 5

# 9pm on March 1, 2017 (local time)
TEST_DATETIME = datetime(2017, 3, 1, 21, 0, 0)
TEST_DATETIME_STRING = datetime.strftime(TEST_DATETIME, BOOTSTRAP_DTIME_FORMAT)

# test lat/lngs: johannesburg
J_LAT = -26.2041
J_LNG = 28.0473
J_STF = StarField(lat=J_LAT, lng=J_LNG, max_mag=MAX_MAG, 
                  localtime_string=TEST_DATETIME_STRING)

# test lat/lngs: sf
SF_LAT = 37.7749
SF_LNG = -122.4194
SF_STF = StarField(lat=SF_LAT, lng=SF_LNG, max_mag=MAX_MAG, 
                    localtime_string=TEST_DATETIME_STRING)


class MarginTestCase(unittest.TestCase):
    """Parent class for tests that need a margin assertion"""

    def assertWithinMargin(self, actual, expected, allowed_margin):
        """Test whether two values are within an acceptable margin

        TODO: make custom exception here."""

        margin = abs(actual - expected)

        self.assertTrue(margin < allowed_margin)


class DbTestCase(MarginTestCase):
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
    # from tests.seed_tests import SeedTestsWithoutDb, SeedTestsWithDb, \
    #     SeedConstellationTests, SeedStarTests, SeedConstLineTests
    # from tests.starfield_tests import StarFieldTestsWithoutDb
    from tests.star_const_tests import StarDataTests, ConstellationDataTests
    # from tests.flask_tests import FlaskTests, FlaskTestsWithDb

    # run the tests
    unittest.main()
