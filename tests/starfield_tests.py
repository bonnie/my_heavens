"""Tests for the Starfield code."""

from unittest import TestCase
import math
from datetime import datetime

# be able to import from parent dir
import sys
sys.path.append('..')

from starfield import Starfield
from run_tests import DbTestCase

TEST_RADIUS = 100
MAX_MAG = 5

# 9pm PST on March 1, 2017 (which is 5am on March 2 in utc)
TEST_DATETIME = datetime(2017, 3, 2, 5, 0, 0)

# test lat/lngs: johannesburg
J_LAT = -26.2041
J_LNG = 28.0473
J_LAT_RAD = -0.45734782252184614
J_LNG_RAD = 0.4895177312946056

# test lat/lngs: sf
SF_LAT = 37.7749
SF_LNG = -122.4194
SF_LAT_RAD = 0.659296379611606
SF_LNG_RAD = 4.14656370886364

# Rigel
R_RA = 1.372
R_DEC = -0.143

# Alpha Tel
AT_RA = 4.851
AT_DEC = -0.801


class StarfieldTestsWithoutDb(TestCase):  
    """Test calculations to retrieve star and constellation data.

    This class is for tests that do not require the database.
    """

    #########################################################
    # Lat/Lng from degrees to radians 
    #########################################################

    def update_latlng_rads_test(self, lat, lng, expected_lat_rad, expected_lng_rad):
        """generalized test for translating lat and lng to radians"""

        # this is a little artificial, to set the lat and lng directly, but it's
        # the only way to separate out this method from __init__
        starf = Starfield(0, 0)
        starf.lat = lat
        starf.lng = lng

        starf.update_latlng_rads()

        self.assertEqual(starf.lat, expected_lat_rad)
        self.assertEqual(starf.lng, expected_lng_rad)


    def test_latlng_rad_SF(self):
        """Test translating latitude (north) and longitude (west) to radians.
        """

        # san francisco
        self.update_latlng_rads_test(SF_LAT, SF_LNG, SF_LAT_RAD, SF_LNG_RAD)


    def test_latlng_rad_Johannesburg(self):
        """Test translating latitude (south) and longitude (east) to radians.
        """

        # johannesburg
        self.update_latlng_rads_test(J_LAT, J_LNG, J_LAT_RAD, J_LNG_RAD)



