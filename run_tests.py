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
from model import db, connect_to_db
from server import app
from seed import load_seed_data

TESTDB_URI = 'postgresql:///star_tests'
TESTDATA_DIR = 'tests/test_data'
MAX_MAG = 5

# for both planets and stars -- needed for both starfield and star_const tests
COORDS_KEY_SET = set(['ra', 'dec'])
SKYOBJECT_KEY_SET = COORDS_KEY_SET | set(['color', 'magnitude', 'name',
    'distance', 'celestialType', 'distanceUnits', 'constellation'])


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
    from tests.seed_tests import SeedTestsWithoutDb, SeedTestsWithDb, \
        SeedConstellationTests, SeedStarTests, SeedConstLineTests
    from tests.starfield_tests import StarFieldTestsWithoutDb
    from tests.star_const_tests import StarDataTests, ConstellationDataTests, \
        SerpensConstellationDataTests
    from tests.model_tests import ModelReprTests
    from tests.flask_tests import FlaskHTMLTests, FlaskDefinitionTests, \
        FlaskStarDataTests, FlaskPlacetimeDataTests

    # run the tests
    unittest.main()
