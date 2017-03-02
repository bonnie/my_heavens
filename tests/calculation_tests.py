"""Tests for the calculations code."""

from unittest import TestCase
import math

# be able to import from parent dir
import sys
sys.path.append('..')

import calculations as calc
from model import db
from run_tests import DbTestCase

TEST_RADIUS = 100


class CalculationTestsWithoutDb(TestCase):  
    """Test calculations to retrieve star and constellation data.

    This class is for tests that do not require the database.
    """

    def pol2cart_test(self, rho, phi, expected_x, expected_y):
        """generalized pol2cart test to avoid repeated code"""

        x, y = calc.pol2cart(rho, phi, TEST_RADIUS)

        self.assertEqual(x, expected_x)
        self.assertEqual(y, expected_y)


    def test_pol2cart_north_horizon(self):
        """Test polar to cartesian coordinates, for a point on northern horizon.
        """

        self.pol2cart_test(rho=TEST_RADIUS,
                           phi=0,
                           expected_x=TEST_RADIUS,
                           expected_y=0)


    def test_pol2cart_overhead(self):
        """Test polar to cartesian coordinates, for a point straight overhead.

        phi is negative for this test.
        """

        self.pol2cart_test(rho=0,
                           phi=0,
                           expected_x=TEST_RADIUS,
                           expected_y=TEST_RADIUS)


    def test_pol2cart_neg_phi(self): 
        """Test polar to cartesian coordinates for negative phi.
        """

        self.pol2cart_test(rho=TEST_RADIUS / 2,
                           phi=-math.pi / 2,
                           expected_x=TEST_RADIUS * 3/2,
                           expected_y=TEST_RADIUS)


class CalculationTestsWithDb(DbTestCase):  
    """Test calculations to retrieve star and constellation data.

    This class is for tests requiring the database.
    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(CalculationTestsWithDb, cls).setUpClass()
        super(CalculationTestsWithDb, cls).load_test_data()

