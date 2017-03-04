"""Tests for the Starfield code."""

from unittest import TestCase
import math
from datetime import datetime

# be able to import from parent dir
import sys
sys.path.append('..')

from model import Constellation
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
J_STF = StarField(lat=J_LAT, lng=J_LNG, utctime=TEST_DATETIME, 
                    display_radius=TEST_RADIUS, max_mag=MAX_MAG)

# test lat/lngs: sf
SF_LAT = 37.7749
SF_LNG = -122.4194
SF_LAT_RAD = 0.659296379611606
SF_LNG_RAD = 4.14656370886364
SF_STF = StarField(lat=SF_LAT, lng=SF_LNG, utctime=TEST_DATETIME,
                     display_radius=TEST_RADIUS, max_mag=MAX_MAG)

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
        stf = StarField(lat=0, lng=0, display_radius=TEST_RADIUS)
        stf.lat = lat
        stf.lng = lng

        stf.update_latlng_rads()

        self.assertEqual(stf.lat, expected_lat_rad)
        self.assertEqual(stf.lng, expected_lng_rad)


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

        # dummy stfield to use for the radius
        stf = StarField(lat=0, lng=0, display_radius=TEST_RADIUS)
        x, y = stf.pol2cart(rho, phi)

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

    def star_coords_test(self, stf, ra, dec, 
                         expected_x, expected_y, expected_visible,
                         calculate_invisible):

        out = stf.get_display_coords(ra, dec, calculate_invisible)

        self.assertEqual(out['x'], expected_x)
        self.assertEqual(out['y'], expected_y)
        self.assertEqual(out['visible'], expected_visible)


    def test_altel_sf_position_calculate_invisible(self):
        """Test calculation of x, y, visible for Alpha Tel in SF at TEST_DATETIME.

        Calculate coords even though it's invisible."""

        stf = SF_STF

        # expected outcomes
        x = -39.225014668891333
        y = 221.53911897280611
        vis = False

        self.star_coords_test(SF_STF, AT_RA, AT_DEC, x, y, vis,
                              calculate_invisible=True)


    def test_altel_sf_position_skip_invisible_calculation(self):
        """Test calculation of x, y, visible for Alpha Tel in SF at TEST_DATETIME.

        Only calculate coords if visible."""

        # expected outcomes
        x = None
        y = None
        vis = False

        self.star_coords_test(SF_STF, AT_RA, AT_DEC, x, y, vis,
                              calculate_invisible=False)


    def test_altel_johannesburg_position(self):
        """Test calculation of x, y, visible for Alpha Tel in Johannesburg at TEST_DATETIME."""

        # expected outcomes
        x = 88.44111905561941
        y = 122.69134380242504
        vis = True

        self.star_coords_test(J_STF, AT_RA, AT_DEC, x, y, vis,
                              calculate_invisible=True)


    def test_rigel_johannesburg_position_calculate_invisible(self):
        """Test calculation of x, y, visible for Rigel in Johannesburg at TEST_DATETIME.

        Calculate coords even though it's invisible."""

        # expected outcomes
        x = 77.386186324330623
        y = 259.86531235645788
        vis = False

        self.star_coords_test(J_STF, R_RA, R_DEC, x, y, vis,
                              calculate_invisible=True)


    def test_rigel_johannesburg_position_skip_invisible_calculation(self):
        """Test calculation of x, y, visible for Rigel in Johannesburg at TEST_DATETIME.

        Only calculate coords if visible."""

        # expected outcomes
        x = None
        y = None
        vis = False

        self.star_coords_test(J_STF, R_RA, R_DEC, x, y, vis,
                              calculate_invisible=False)


class StarFieldStarDataTests(DbTestCase):
    """Test calculations for stfield star data

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(StarFieldStarDataTests, cls).setUpClass()
        super(StarFieldStarDataTests, cls).load_test_data()
        cls.stf = SF_STF
        cls.stars = cls.stf.get_stars()
        cls.example_star = cls.stars[0]


    def test_star_count(self):
        """Test the star count for the star field."""

        # we expect 48 stars for the test data set, San Francisco, TEST_DATETIME
        self.assertEqual(len(self.stars), 48)


    def test_star_data_type(self):
        """Test the that the example star is a dict."""

        self.assertIsInstance(self.example_star, dict)


    def test_star_keys(self):
        """Test the keys of the star dict of the first item in self.stars."""

        star_keys = set(self.example_star.keys())
        expected_keys = set(['x', 'y', 'magnitude', 'color', 'name'])
        self.assertEqual(star_keys, expected_keys)


    def test_max_magnitude(self):
        """Test that no star's magnitude exceeds the maximum magnitude."""

        mags_over_max = [ star['magnitude'] for star in self.stars 
                          if star['magnitude'] > self.stf.max_mag ]

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
        cls.ori = Constellation.query.filter_by(const_code='ORI').one()
        cls.tel = Constellation.query.filter_by(const_code='TEL').one()
        cls.expected_const_keys = set(['bound_verts', 'line_groups', 'code', 'name'])


    #########################################################
    # Constellation Line Groups
    #########################################################

    def test_get_const_line_groups_types(self):
        """Make sure the function is returning data in the expected formats"""

        visible, line_groups = SF_STF.get_const_line_groups(self.ori)

        example_group = line_groups[0]
        example_vertex = example_group[0]

        self.assertIsInstance(visible, bool)
        self.assertIsInstance(line_groups, list) 
        self.assertIsInstance(example_group, list) 
        self.assertIsInstance(example_vertex, dict) 
        self.assertEqual(set(example_vertex.keys()), set(['x', 'y']))


    def const_line_groups_test(self, stf, const, expected_count, expected_vis):
        """Test constellation line groups for various inputs"
        """

        visible, line_groups = stf.get_const_line_groups(const)

        self.assertEqual(visible, expected_vis)
        if visible: 
            self.assertEqual(len(line_groups), expected_count)


    def test_const_line_groups_sf_ori(self):
        """Test constellation line groups for multi-group, visible"""

        self.const_line_groups_test(SF_STF, self.ori, 
                                    expected_count=4, 
                                    expected_vis=True)


    def test_const_line_groups_sf_tel(self):
        """Test constellation line groups for single-group, not visible"""

        self.const_line_groups_test(SF_STF, self.tel, 
                                    expected_count=0, 
                                    expected_vis=False)


    def test_const_line_groups_jo_ori(self):
        """Test constellation line groups for multi-group, not visible"""

        self.const_line_groups_test(J_STF, self.ori, 
                                    expected_count=0, 
                                    expected_vis=False)


    def test_const_line_groups_jo_ori(self):
        """Test constellation line groups for single-group, visible"""

        self.const_line_groups_test(J_STF, self.tel, 
                                    expected_count=1, 
                                    expected_vis=True)

        
#### TODO: test constellation that's half on / half off

    #########################################################
    # Constellation Boundaries
    #########################################################

    def test_get_const_bound_verts_types(self):
        """Make sure the function is returning data in the expected formats"""

        bound_verts = SF_STF.get_const_bound_verts(self.ori)

        example_vertex = bound_verts[0]

        self.assertIsInstance(bound_verts, list)
        self.assertIsInstance(example_vertex, dict) 
        self.assertEqual(set(example_vertex.keys()), set(['x', 'y']))


    def const_bound_verts_test(self, stf, const, expected_count):
        """Generic test for constellation boundary data."""

        verts = stf.get_const_bound_verts(const)
        self.assertEqual(len(verts), expected_count)

        # check that th last vertex is a repeat of the first
        self.assertEqual(verts[0], verts[-1])


    def test_sf_ori_bound_verts(self):
        """Test bound vertices for Orion. Starfield doesn't matter for this test
        """

        self.const_bound_verts_test(SF_STF, self.ori, 29)


    def test_sf_tel_bound_verts(self):
        """Test bound vertices for Tel. Starfield doesn't matter for this test.
        """

        self.const_bound_verts_test(SF_STF, self.tel, 6)


    #########################################################
    # Constellation Data
    #########################################################

    def test_get_const_data_types(self):
        """Make sure the function is returning data in the expected formats"""

        const_data = SF_STF.get_const_data(self.ori)

        example_bound_verts = const_data['bound_verts']
        example_bound_vertex = example_bound_verts[0]
        example_line_groups = const_data['line_groups']
        example_line_group = example_line_groups[0]
        example_line_vertex = example_line_group[0]

        self.assertIsInstance(const_data, dict) 
        self.assertEqual(set(const_data.keys()), self.expected_const_keys)

        self.assertIsInstance(example_bound_verts, list) 
        self.assertIsInstance(example_bound_vertex, dict) 
        self.assertEqual(set(example_bound_vertex.keys()), set(['x', 'y']))

        self.assertIsInstance(example_line_groups, list) 
        self.assertIsInstance(example_line_group, list) 
        self.assertIsInstance(example_line_vertex, dict) 
        self.assertEqual(set(example_line_vertex.keys()), set(['x', 'y']))


    def get_const_data_test(self, stf, const, expected_type, expected_name):
        """Generic function for getting constellation data"""

        const_data = stf.get_const_data(const)

        self.assertIsInstance(const_data, expected_type)

        if expected_type == dict:
            self.assertEqual(const_data['name'], expected_name)


    def test_get_const_sf_ori(self):
        """Test data returned for orion in sf."""

        self.get_const_data_test(SF_STF, self.ori, dict, 'Orion')


    def test_get_const_sf_tel(self):
        """Test data returned for orion in sf."""

        self.get_const_data_test(SF_STF, self.tel, type(None), None)


    def test_get_const_johannesburg_ori(self):
        """Test data returned for orion in sf."""

        self.get_const_data_test(J_STF, self.ori, type(None), None)


    def test_get_const_johannesburg_tel(self):
        """Test data returned for orion in sf."""

        self.get_const_data_test(J_STF, self.tel, dict, 'Telescopium')


    #########################################################
    # Constellation List
    #########################################################

    def test_get_consts_types(self):
        """Make sure the function is returning data in the expected formats"""

        consts = SF_STF.get_consts()
        example_const = consts[0]

        self.assertIsInstance(consts, list) 
        self.assertIsInstance(example_const, dict) 
        self.assertEqual(set(example_const.keys()), self.expected_const_keys)


    def test_sf_consts(self):
        """Test data returned for constellations in SF."""

        consts = SF_STF.get_consts()

        self.assertEqual(len(consts), 1)
        self.assertEqual(consts[0]['name'], 'Orion')


    def test_johannesburg_consts(self):
        """Test data returned for constellations in Johannesburg."""

        consts = J_STF.get_consts()

        self.assertEqual(len(consts), 1)
        self.assertEqual(consts[0]['name'], 'Telescopium')
