"""Tests for the Starfield code.

    Copyright (c) 2017 Bonnie Schulkin

    This file is part of My Heavens.

    My Heavens is free software: you can redistribute it and/or modify it under
    the terms of the GNU Affero General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option)
    any later version.

    My Heavens is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
    for more details.

    You should have received a copy of the GNU Affero General Public License
    along with My Heavens. If not, see <http://www.gnu.org/licenses/>.

"""

from unittest import TestCase
import math
from datetime import datetime
import pytz
import ephem

# be able to import from parent dir
import sys
sys.path.append('..')

from model import Constellation
from starfield import deg_to_rad, StarField, BOOTSTRAP_DTIME_FORMAT
from run_tests import MarginTestCase, DbTestCase

MAX_MAG = 5

# acceptable margin when comparing floats
MARGIN = 0.005

# 9pm on March 1, 2017 (local time)
TEST_DATETIME = datetime(2017, 3, 1, 21, 0, 0)
TEST_DATETIME_STRING = datetime.strftime(TEST_DATETIME, BOOTSTRAP_DTIME_FORMAT)

# expected data sets
CONST_LIST_SET = set(['Orion', 'Monoceros', 'Telescopium'])
COORDS_KEY_SET = set(['ra', 'dec'])
SKYOBJECT_KEY_SET = COORDS_KEY_SET | set(['color', 'magnitude', 'name'])
PLANET_KEY_SET = SKYOBJECT_KEY_SET | set(['size'])

# expected planets for star field settings 
BRIGHT_PLANET_NAMES_SET = set(['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Sun'])

# test lat/lngs: johannesburg
J_LAT = -26.2041
J_LNG = 28.0473
J_LAT_RAD = -0.45734782252184614
J_LNG_RAD = 0.4895177312946056
J_STF = StarField(lat=J_LAT, lng=J_LNG, max_mag=MAX_MAG, 
                  localtime_string=TEST_DATETIME_STRING)

# test lat/lngs: sf
SF_LAT = 37.7749
SF_LNG = -122.4194
SF_LAT_RAD = 0.659296379611606
SF_LNG_RAD = 4.14656370886364
SF_STF = StarField(lat=SF_LAT, lng=SF_LNG, max_mag=MAX_MAG, 
                    localtime_string=TEST_DATETIME_STRING)

# Rigel
R_RA = 1.372
R_DEC = -0.143

# Alpha Tel
AT_RA = 4.851
AT_DEC = -0.801


class StarFieldTestsWithoutDb(MarginTestCase):  
    """Test calculations to retrieve star and constellation data.

    This class is for tests that do not require the database.
    """

    #########################################################
    # degrees -> radians utility function
    #########################################################

    def test_deg_to_rad_positive(self):
        """Test a positive degrees -> radians conversion."""

        rads = deg_to_rad(2.5)
        self.assertEqual(rads, math.pi / 82)


    def test_deg_to_rad_negative(self):
        """Test a negative degrees -> radians conversion."""

        rads = rad_to_deg(-180)
        self.assertEqual(rads, -math.pi)


    def test_deg_to_rad_zero(self):
        """Test a zero degrees -> radians conversion."""

        rads = rad_to_deg(0)
        self.assertEqual(rads, 0)


    #########################################################
    # starfield time zones
    #########################################################

    def test_sf_timezone(self):
        """Test getting time zone for san francisco."""

        tz = SF_STF.get_timezone()
        self.assertEqual(tz.zone, 'America/Los_Angeles')


    def test_johannesburg_timezone(self):
        """Test getting time zone for san francisco."""

        tz = J_STF.get_timezone()
        self.assertEqual(tz.zone, 'Africa/Johannesburg')


    def test_zero_zero_timezone(self):
        """Test getting time zone for lat/lng that has no time zone.

        In this case, we return utc."""

        stf = StarField(lat=0, lng=0)
        tz = stf.get_timezone()
        self.assertEqual(tz.zone, 'Etc/UTC')


    #########################################################
    # starfield with no time provided
    #########################################################

    def test_no_time_provided(self):
        """Test that a starfield gets the time of "now" if no time is provided"""

        stf = StarField(lat=SF_LAT, lng=SF_LNG)
        now = datetime.utcnow()

        # make sure the time assigned is no more than one second off current time
        self.assertTrue(abs(stf.utctime - now).seconds < 1)


    #########################################################
    # local time to utc
    #########################################################

    def local_to_utc_time_test(self, lat, lng, expected_offset):
        """A generic function to test the starfield set_utc_time method

        expected_offset is a time difference from UTC, in hours"""

        # make a starfield instance with an arbitrary time
        now_string = datetime.strftime(datetime.now(), BOOTSTRAP_DTIME_FORMAT)
        stf = StarField(lat=lat, lng=lng, localtime_string=now_string)

        stf.set_utc_time(TEST_DATETIME_STRING)
        time_diff = stf.utctime - pytz.utc.localize(TEST_DATETIME)
        self.assertEqual(time_diff.seconds, expected_offset * 3600)


    def test_sf_localtime_to_utc(self):
        """Test translating sf localtime to utc."""

        self.local_to_utc_time_test(SF_LAT, SF_LNG, 8)


    def test_johannesburg_localtime_to_utc(self):
        """Test translating johannesburg localtime to utc.

        Note: it won't be a day ahead because of the way I'm testing 
        (hence the 22 instead of -2 for the offset)"""

        self.local_to_utc_time_test(J_LAT, J_LNG, 22)


    #########################################################
    # Star coords based on location, time, ra, dec
    #########################################################

    def star_coords_test(self, stf, ra, dec, expected_alt, expected_az):

        altaz = stf.get_display_coords(ra, dec)

        self.assertEqual(altaz['alt'], expected_alt)
        self.assertEqual(altaz['az'], expected_az)


    def test_rigel_sf_position(self):
        """Test calculation of alt/az for Rigel in SF at TEST_DATETIME."""

        # expected outcomes
        alt = 0.5945513722730493
        az = 3.8768423769051004

        self.star_coords_test(SF_STF, R_RA, R_DEC, alt, az)


    def test_altel_sf_position(self):
        """Test calculation of alt/az for Alpha Tel in SF at TEST_DATETIME."""

        # expected outcomes
        alt = -1.33221897026607
        az = 2.28847485543228

        self.star_coords_test(SF_STF, AT_RA, AT_DEC, alt, az)


    def test_altel_johannesburg_position(self):
        """Test calculation of alt/az for Alpha Tel in Johannesburg at TEST_DATETIME."""

        # expected outcomes
        alt = -0.29052825967453816
        az = 2.953992076759778

        self.star_coords_test(J_STF, AT_RA, AT_DEC, alt, az)


    def test_rigel_johannesburg_position(self):
        """Test calculation of alt/az for Rigel in Johannesburg at TEST_DATETIME."""

        # expected outcomes
        alt = 0.9229068038241716
        az = 5.109812449003042 

        self.star_coords_test(J_STF, R_RA, R_DEC, alt, az)



    #########################################################
    # making pyEphem ephemeris
    #########################################################

    def make_ephem_test(self, stf):
        """Generic test for making a pyEphem ephemeris."""

        stf.make_ephem()
        self.assertIsInstance(stf.ephem, ephem.Observer)


    def test_sf_ephem(self):
        """Test making ephemeris for SF."""

        self.make_ephem_test(SF_STF)


    def test_johannesburg_ephem(self):
        """Test making ephemeris for Johannesburg."""

        self.make_ephem_test(J_STF)


    #########################################################
    # individual planet data tests
    #########################################################

    def test_planet_data_format(self):
        """Test the format of data returned from get_planet_data."""

        # actual stf and planet are inconsequential here
        pdata = SF_STF.get_planet_data(ephem.Mars)

        self.assertIsInstance(pdata, dict)
        self.assertEqual(set(pdata.keys()), PLANET_KEY_SET)
        self.assertIsInstance(pdata['alt'], float)
        self.assertIsInstance(pdata['az'], float)
        self.assertIsInstance(pdata['magnitude'], float)
        self.assertIsInstance(pdata['name'], str)
        self.assertEqual(pdata['color'][0], '#') # color should be a hex color string
        self.assertIsInstance(pdata['size'], float)


    def get_planet_data_test(self, stf, planet, expected_alt, expected_az):
        """Generic test for getting planet data."""

        pdata = stf.get_planet_data(planet)

        self.assertEqual(pdata['alt'], expected_alt)
        self.assertEqual(pdata['az'], expected_az)

        # as a sanity check, check to see that the ephem translated the 
        # ra/dec to alt/az simliarly to my display function
        # TODO: figure out why this doesn't work for johannesburg mars alt, 
        # and why in general the az's are all very close but the alts are farther off

        # ephem_data = planet(stf.ephem)
        # self.assertWithinMargin(ephem_data.alt, expected_alt, MARGIN)
        # self.assertWithinMargin(ephem_data.az, expected_az, MARGIN)


    def test_sf_mars_data(self):
        """Test position of mars for SF, visible at test datetime."""

        # expected data
        alt = 0.09758790174682835
        az = 4.846001800860591

        self.get_planet_data_test(SF_STF, ephem.Mars, alt, az)


    def test_sf_saturn_data(self):
        """Test position of saturn for SF, not visible at test datetime."""

        # expected data
        alt = -1.091673576190396
        az = 1.093068434224584

        self.get_planet_data_test(SF_STF, ephem.Saturn, alt, az)


    def test_johannesburg_mars_data(self):
        """Test position of mars for johannesburg, not visible at test datetime."""

        # expected data
        alt = -0.08086610293050318
        az = 4.854684008179456

        self.get_planet_data_test(J_STF, ephem.Mars, alt, az)


    def test_johannesburg_jupiter_data(self):
        """Test position of jupiter for johannesburg, visible at test datetime."""

        # expected data
        alt = 0.08146127157074838
        az = 1.6721818546910152

        self.get_planet_data_test(J_STF, ephem.Jupiter, alt, az)


    #########################################################
    # collective planet data tests
    #########################################################

    def get_planets_test(self, stf):
        """Generic test to get planets."""

        planets = stf.get_planets()

        # get a set of the planet names
        planet_names = set(p['name'] for p in planets)

        self.assertEqual(planet_names, BRIGHT_PLANET_NAMES_SET)


    #########################################################
    # moon data tests
    #########################################################

    # TODO: add moon data tests once I've settled on moon data
    def test_moon_data_format(self):
        """Test format of returned moon data."""


    def moon_data_test(self, stf, expected_alt, expected_az, expected_phase):
        """Generic test for moon data."""


    def test_sf_moon_data(self):
        """Test moon data for San Francisco."""

        # expected data
        alt = 0
        az = 0
        phase = 0

        self.moon_data_test(SF_STF, alt, az, phase)


    def test_johannesburg_moon_data(self):
        """Test moon data for Johannesburg"""

        # expected data
        alt = 0
        az = 0
        phase = 0

        self.moon_data_test(J_STF, alt, az, phase)


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

        # we expect 55 stars for the test data set, San Francisco, TEST_DATETIME
        self.assertEqual(len(self.stars), 55)


    def test_star_data_type(self):
        """Test the that the example star is a dict."""

        self.assertIsInstance(self.example_star, dict)


    def test_star_keys(self):
        """Test the keys of the star dict of the first item in self.stars."""

        star_keys = set(self.example_star.keys())
        expected_keys = SKYOBJECT_KEY_SET
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

        line_groups = SF_STF.get_const_line_groups(self.ori)

        example_group = line_groups[0]
        example_vertex = example_group[0]

        self.assertIsInstance(line_groups, list) 
        self.assertIsInstance(example_group, list) 
        self.assertIsInstance(example_vertex, dict) 
        self.assertEqual(set(example_vertex.keys()), COORDS_KEY_SET)


    def const_line_groups_test(self, stf, const, expected_count):
        """Test constellation line groups for various inputs"
        """

        line_groups = stf.get_const_line_groups(const)
        self.assertEqual(len(line_groups), expected_count)


    def test_const_line_groups_sf_ori(self):
        """Test constellation line groups for multi-group, visible"""

        self.const_line_groups_test(SF_STF, self.ori, expected_count=4)


    def test_const_line_groups_sf_tel(self):
        """Test constellation line groups for single-group, not visible"""

        self.const_line_groups_test(SF_STF, self.tel, expected_count=1)


    def test_const_line_groups_jo_ori(self):
        """Test constellation line groups for multi-group, not visible"""

        self.const_line_groups_test(J_STF, self.ori, expected_count=4)


    def test_const_line_groups_jo_ori(self):
        """Test constellation line groups for single-group, visible"""

        self.const_line_groups_test(J_STF, self.tel, expected_count=1)


    #########################################################
    # Constellation Boundaries
    #########################################################

    def test_get_const_bound_verts_types(self):
        """Make sure the function is returning data in the expected formats"""

        bound_verts = SF_STF.get_const_bound_verts(self.ori)

        example_vertex = bound_verts[0]

        self.assertIsInstance(bound_verts, list)
        self.assertIsInstance(example_vertex, dict) 
        self.assertEqual(set(example_vertex.keys()), COORDS_KEY_SET)


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
        self.assertEqual(set(example_bound_vertex.keys()), COORDS_KEY_SET)

        self.assertIsInstance(example_line_groups, list) 
        self.assertIsInstance(example_line_group, list) 
        self.assertIsInstance(example_line_vertex, dict) 
        self.assertEqual(set(example_line_vertex.keys()), COORDS_KEY_SET)


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
        """Test data returned for telescopium in sf."""

        self.get_const_data_test(SF_STF, self.tel, dict, 'Telescopium')


    def test_get_const_johannesburg_ori(self):
        """Test data returned for orion in johannesburg."""

        self.get_const_data_test(J_STF, self.ori, dict, 'Orion')


    def test_get_const_johannesburg_tel(self):
        """Test data returned for telescopium in johannesburg."""

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


    def const_list_test(self, stf):
        """Generic test for returning constellation list. 

        Output should be the same regardless of starfield constraints."""

        consts = stf.get_consts()

        # get the list of names with a set comprehension
        const_names = set(const['name'] for const in consts)

        self.assertEqual(len(consts), 3)
        self.assertEqual(const_names, CONST_LIST_SET)


    def test_sf_consts(self):
        """Test data returned for constellations in SF."""

        self.const_list_test(SF_STF)


    def test_johannesburg_consts(self):
        """Test data returned for constellations in Johannesburg."""

        self.const_list_test(J_STF)

