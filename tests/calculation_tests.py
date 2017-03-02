"""Tests for the calculations code."""

from unittest import TestCase
import math
from datetime import datetime

# be able to import from parent dir
import sys
sys.path.append('..')

import calculations as calc
from model import db
from run_tests import DbTestCase

TEST_RADIUS = 100

# 9pm PST on March 1, 2017 (which is 5am on March 2 in utc)
TEST_DATETIME = datetime(2017, 3, 2, 5, 0, 0)

# test lat/lngs: johannesburg
J_LAT = '26.2041dS'
J_LNG = '28.0473dE'

# test lat/lngs: sf
SF_LAT = '37.7749dN'
SF_LNG = '122.4194dW'

class CalculationTestsWithoutDb(TestCase):  
    """Test calculations to retrieve star and constellation data.

    This class is for tests that do not require the database.
    """

    ################################
    # Generic tests for repetition #
    ################################

    def pol2cart_test(self, rho, phi, expected_x, expected_y):
        """generalized pol2cart test to avoid repeated code"""

        x, y = calc.pol2cart(rho, phi, TEST_RADIUS)

        self.assertEqual(x, expected_x)
        self.assertEqual(y, expected_y)


    def rad_translation_test(self, lat, lng, expected_lat_rad, expected_lng_rad):
        """generalized test for translating lat and lng to radians"""

        lat_rad, lng_rad = calc.get_latlng_rads(lat, lng)

        self.assertEqual(lat_rad, expected_lat_rad)
        self.assertEqual(lng_rad, expected_lng_rad)


    # def star_coords_test(self)

    #     x, y, visible = calc.get_star_coords()



    ################
    # Test methods #
    ################

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


    def test_latlng_rad_SF(self):
        """Test translating latitude (north) and longitude (west) to radians.
        """

        # san francisco
        self.rad_translation_test(lat=SF_LAT,
                                  lng=SF_LNG,
                                  expected_lat_rad=0.659296379611606,
                                  expected_lng_rad=4.14656370886364)

    def test_latlng_rad_Johannesburg(self):
        """Test translating latitude (south) and longitude (east) to radians.
        """

        # johannesburg
        self.rad_translation_test(lat=J_LAT,
                                  lng=J_LNG,
                                  expected_lat_rad=-0.45734782252184614,
                                  expected_lng_rad=0.4895177312946056)



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

