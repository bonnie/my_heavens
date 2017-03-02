"""Tests for the Starfield code."""

from unittest import TestCase
import math
from datetime import datetime

# be able to import from parent dir
import sys
sys.path.append('..')

from starfield import StarField
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
J_STARF = StarField(lat=J_LAT, lng=J_LNG, utctime=TEST_DATETIME, display_radius=TEST_RADIUS)

# test lat/lngs: sf
SF_LAT = 37.7749
SF_LNG = -122.4194
SF_LAT_RAD = 0.659296379611606
SF_LNG_RAD = 4.14656370886364
SF_STARF = StarField(lat=SF_LAT, lng=SF_LNG, utctime=TEST_DATETIME, display_radius=TEST_RADIUS)


# Rigel
R_RA = 1.372
R_DEC = -0.143

# Alpha Tel
AT_RA = 4.851
AT_DEC = -0.801


class StarFieldTestsWithoutDb(TestCase):  
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
        starf = StarField(lat=0, lng=0)
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


    #########################################################
    # Polar to Cartesian Tests 
    #########################################################

    def pol2cart_test(self, rho, phi, expected_x, expected_y):
        """generalized pol2cart test to avoid repeated code"""

        # dummy starfield to use for the radius
        starf = StarField(lat=0, lng=0, display_radius=TEST_RADIUS)
        x, y = starf.pol2cart(rho, phi)

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


    #########################################################
    # Star coords based on location, time, ra, dec
    #########################################################

    def star_coords_test(self, starf, ra, dec, 
                         expected_x, expected_y, expected_visible,
                         calculate_invisible):

        out = starf.get_display_coords(ra, dec, calculate_invisible)

        self.assertEqual(out['x'], expected_x)
        self.assertEqual(out['y'], expected_y)
        self.assertEqual(out['visible'], expected_visible)


    def test_altel_sf_position_calculate_invisible(self):
        """Test calculation of x, y, visible for Alpha Tel in SF at TEST_DATETIME.

        Calculate coords even though it's invisible."""

        starf = SF_STARF

        # expected outcomes
        x = -39.225014668891333
        y = 221.53911897280611
        vis = False

        self.star_coords_test(SF_STARF, AT_RA, AT_DEC, x, y, vis,
                              calculate_invisible=True)


    def test_altel_sf_position_skip_invisible_calculation(self):
        """Test calculation of x, y, visible for Alpha Tel in SF at TEST_DATETIME.

        Only calculate coords if visible."""

        # expected outcomes
        x = None
        y = None
        vis = False

        self.star_coords_test(SF_STARF, AT_RA, AT_DEC, x, y, vis,
                              calculate_invisible=False)


    def test_altel_johannesburg_position(self):
        """Test calculation of x, y, visible for Alpha Tel in Johannesburg at TEST_DATETIME."""

        # expected outcomes
        x = 88.44111905561941
        y = 122.69134380242504
        vis = True

        self.star_coords_test(J_STARF, AT_RA, AT_DEC, x, y, vis,
                              calculate_invisible=True)


    def test_rigel_johannesburg_position_calculate_invisible(self):
        """Test calculation of x, y, visible for Rigel in Johannesburg at TEST_DATETIME.

        Calculate coords even though it's invisible."""

        # expected outcomes
        x = 77.386186324330623
        y = 259.86531235645788
        vis = False

        self.star_coords_test(J_STARF, R_RA, R_DEC, x, y, vis,
                              calculate_invisible=True)


    def test_rigel_johannesburg_position_skip_invisible_calculation(self):
        """Test calculation of x, y, visible for Rigel in Johannesburg at TEST_DATETIME.

        Only calculate coords if visible."""

        # expected outcomes
        x = None
        y = None
        vis = False

        self.star_coords_test(J_STARF, R_RA, R_DEC, x, y, vis,
                              calculate_invisible=False)


class StarFieldStarDataTests(DbTestCase):
    """Test calculations for starfield star data

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(StarFieldStarDataTests, cls).setUpClass()
        super(StarFieldStarDataTests, cls).load_test_data()
        cls.stars = SF_STARF.get_star_data()
        cls.example_star = cls.stars[0]


    def test_star_count(self):
        """Test the star count for the star field."""

        # we expect 48 stars for the test data set, San Francisco, TEST_DATETIME
        self.assertEqual(len(self.stars), 48)


    def test_star_data_type(self):
        """Test the that the example star is a dict."""

        self.assertEqual(type(self.example_star), dict)


    def test_star_keys(self):
        """Test the keys of the star dict of the first item in self.stars."""

        star_keys = set(self.example_star.keys())
        expected_keys = set(['x', 'y', 'magnitude', 'color', 'name'])
        self.assertEqual(star_keys, expected_keys)


    def test_max_magnitude(self):
        """Test that no star's magnitude exceeds the maximum magnitude."""

        mags_over_max = [ star['magnitude'] for star in self.stars 
                          if star['magnitude'] > MAX_MAG ]

        self.assertEqual(mags_over_max, [])


class StarFieldConstellationDataTests(DbTestCase):
    """Test calculations for star and constellation data at a time and place.

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(StarFieldConstellationDataTests, cls).setUpClass()
        super(StarFieldConstellationDataTests, cls).load_test_data()
