"""Tests for star charts app. 

This file simply collects and runs tests in other files (separated for better
organization). It also holds common constants."""

import unittest

TESTDB_URI = 'postgresql:///star_tests'
TESTDATA_DIR = 'tests/test_data'


if __name__ == '__main__':

    # import the tests
    from tests.seed_tests import SeedTestsWithoutDb, SeedTestsWithDb, \
        SeedConstellationTests, SeedStarTests
    from tests.db_tests import DbTests
    from tests.calculation_tests import CalculationTests
    from tests.flask_tests import FlaskTests

    # run the tests
    unittest.main()
