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

import os
from unittest import TestCase
import math
from datetime import datetime
import pytz
import ephem

# be able to import from parent dir
import sys
sys.path.append('..')

from run_tests import MarginTestCase, DbTestCase
from model import Constellation
from starfield import deg_to_rad, rad_to_deg, StarField, BOOTSTRAP_DTIME_FORMAT

MAX_MAG = 5

# acceptable margin when comparing floats
MARGIN = 0.005

# 9pm on March 1, 2017 (local time)
TEST_DATETIME = datetime(2017, 3, 1, 21, 0, 0)
TEST_DATETIME_STRING = datetime.strftime(TEST_DATETIME, BOOTSTRAP_DTIME_FORMAT)

# expected data sets
CONST_LIST_SET = set(['Orion', 'Monoceros', 'Telescopium'])
COORDS_KEY_SET = set(['ra', 'dec'])
SKYOBJECT_KEY_SET = COORDS_KEY_SET | set(['color', 'magnitude', 'name',
    'distance', 'celestialType', 'distanceUnits', 'constellation'])
PLANET_KEY_SET = SKYOBJECT_KEY_SET | set(['size', 'prevRise', 'phase', 'nextSet'])
SUN_KEY_SET = PLANET_KEY_SET
MOON_KEY_SET = PLANET_KEY_SET | set(['colong', 'rotation'])

# expected planets for star field settings 
BRIGHT_PLANET_NAMES_SET = set(['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'])

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
    # degrees -> radians (and reverse) utility functions
    #########################################################

    def test_deg_to_rad_positive(self):
        """Test a positive degrees -> radians conversion."""

        rads = deg_to_rad(90)
        self.assertEqual(rads, math.pi / 2)


    def test_deg_to_rad_negative(self):
        """Test a negative degrees -> radians conversion."""

        rads = deg_to_rad(-180)
        self.assertEqual(rads, -math.pi)


    def test_rad_to_deg_zero(self):
        """Test a zero degrees -> radians conversion."""

        rads = deg_to_rad(0)
        self.assertEqual(rads, 0)


    def test_rad_to_deg_positive(self):
        """Test a positive radians -> degrees conversion."""

        degs = rad_to_deg(math.pi / 2)
        self.assertEqual(degs, 90)


    def test_rad_to_deg_negative(self):
        """Test a negative radians -> degrees conversion."""

        degs = rad_to_deg(-math.pi)
        self.assertEqual(degs, -180)


    def test_deg_to_rad_zero(self):
        """Test a zero radians -> degrees conversion."""

        degs = rad_to_deg(0)
        self.assertEqual(degs, 0)


    #########################################################
    # starfield time zones
    #########################################################

    def timezone_test(self, stf, expected_tz):
        """A generic function to test the timezone determination code."""

        stf.set_timezone()
        self.assertEqual(stf.timezone, expected_tz)

    def test_sf_timezone(self):
        """Test getting time zone for san francisco."""

        self.timezone_test(SF_STF, pytz.timezone('America/Los_Angeles'))

    def test_johannesburg_timezone(self):
        """Test getting time zone for san francisco."""

        self.timezone_test(J_STF, pytz.timezone('Africa/Johannesburg'))

    def test_zero_zero_timezone(self):
        """Test getting time zone for lat/lng that has no time zone.

        In this case, we return utc."""

        stf = StarField(lat=0, lng=0)
        self.timezone_test(stf, pytz.timezone('Etc/UTC'))


    #########################################################
    # starfield with no time provided
    #########################################################

    def test_no_time_provided(self):
        """Test that a starfield gets the time of "now" if no time is provided"""

        stf = StarField(lat=SF_LAT, lng=SF_LNG)
        now = pytz.utc.localize(datetime.utcnow())

        # make sure the time assigned is no more than one second off current time
        self.assertTrue(abs(stf.utctime - now).seconds < 1)


    #########################################################
    # local time to utc
    #########################################################

    def local_to_utc_time_test(self, lat, lng, expected_offset):
        """A generic function to test the starfield set_utc_time method

        expected_offset is a time difference from UTC, in hours"""

        # make a starfield instance with an arbitrary time
        dt_string = datetime.strftime(TEST_DATETIME, BOOTSTRAP_DTIME_FORMAT)
        stf = StarField(lat=lat, lng=lng, localtime_string=dt_string)

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
    # generic solar system data tests
    #########################################################

    def ss_data_format_test(self, key_set, pdata, celestial_type):
        """Generic test for ephemeris data format."""

        self.assertIsInstance(pdata, dict)
        self.assertEqual(set(pdata.keys()), key_set)
        self.assertIsInstance(pdata['ra'], float)
        self.assertIsInstance(pdata['dec'], float)
        self.assertIsInstance(pdata['magnitude'], float)
        self.assertIsInstance(pdata['name'], str)
        self.assertEqual(pdata['color'][0], '#') # color should be a hex color string
        self.assertIsInstance(pdata['size'], float)
        self.assertIsInstance(pdata['distance'], str)
        self.assertIsInstance(pdata['celestialType'], str)
        self.assertIsInstance(pdata['nextSet'], str)
        self.assertEqual(pdata['distanceUnits'], 'AU')
        self.assertIsInstance(pdata['prevRise'], str)
        self.assertIsInstance(pdata['phase'], str)
        self.assertIsInstance(pdata['constellation'], str)
        self.assertEqual(pdata['celestialType'], celestial_type)


    #########################################################
    # individual planet data tests
    #########################################################

    def test_planet_data_format(self):
        """Test the format of data returned from get_planet_data."""
        
        # actual stf and planet are inconsequential here
        pdata = SF_STF.get_planet_data(ephem.Mars)
        self.ss_data_format_test(PLANET_KEY_SET, pdata, 'planet')

    def get_planet_data_test(self, stf, planet, expected_ra, expected_dec):
        """Generic test for getting planet data."""

        pdata = stf.get_planet_data(planet)

        self.assertEqual(pdata['ra'], expected_ra)
        self.assertEqual(pdata['dec'], expected_dec)

    def test_sf_mars_data(self):
        """Test position of mars for SF, visible at test datetime."""

        # expected data
        ra = 337.4816817093629
        dec = 9.466995889404037

        self.get_planet_data_test(SF_STF, ephem.Mars, ra, dec)

    def test_sf_saturn_data(self):
        """Test position of saturn for SF, not visible at test datetime."""

        # expected data
        ra = 93.45764161796552
        dec = -22.089550180792546

        self.get_planet_data_test(SF_STF, ephem.Saturn, ra, dec)

    def test_johannesburg_mars_data(self):
        """Test position of mars for johannesburg, not visible at test datetime."""

        # expected data
        ra = 337.7657593061578
        dec = 9.351677268540211

        self.get_planet_data_test(J_STF, ephem.Mars, ra, dec)

    def test_johannesburg_jupiter_data(self):
        """Test position of jupiter for johannesburg, visible at test datetime."""

        # expected data
        ra = 158.82593840533076
        dec = -7.263921571076729

        self.get_planet_data_test(J_STF, ephem.Jupiter, ra, dec)


    #########################################################
    # collective planet data tests
    #########################################################

    def get_planets_test(self, stf):
        """Generic test to get planets."""

        planets = stf.get_planets()

        # get a set of the planet names
        planet_names = set(p['name'] for p in planets)

        # all suitably bright planets should be returned
        self.assertEqual(planet_names, BRIGHT_PLANET_NAMES_SET)

    def test_johannesburg_planets(self):
        """Test Johannesburg planet set for the test date and time."""

        self.get_planets_test(J_STF)

    def test_sf_planets(self):
        """Test San Francisco planet set for the test date and time."""

        self.get_planets_test(SF_STF)

    #########################################################
    # sun data tests
    #########################################################

    def test_sun_data_format(self):
        """Test format of sun data."""

        sdata = SF_STF.get_sun()
        self.ss_data_format_test(SUN_KEY_SET, sdata, 'star')

    #########################################################
    # moon data tests
    #########################################################

    def test_moon_data_format(self):
        """Test format of returned moon data."""

        mdata = SF_STF.get_moon()
        self.ss_data_format_test(MOON_KEY_SET, mdata, 'moon')

    def test_moon_specific_data_format(self):
        """Test format of data specific to the moon."""

        mdata = SF_STF.get_moon()
        self.assertIsInstance(mdata['colong'], float)
        self.assertIsInstance(mdata['rotation'], float)
        

    # def moon_data_test(self, stf, expected_alt, expected_az, expected_phase):
    #     """Generic test for moon data."""


    # def test_sf_moon_data(self):
    #     """Test moon data for San Francisco."""

    #     # expected data
    #     alt = 0
    #     az = 0
    #     phase = 0

    #     self.moon_data_test(SF_STF, alt, az, phase)


    # def test_johannesburg_moon_data(self):
    #     """Test moon data for Johannesburg"""

    #     # expected data
    #     alt = 0
    #     az = 0
    #     phase = 0

    #     self.moon_data_test(J_STF, alt, az, phase)


class StarFieldStarDataTests(DbTestCase):
    """Test calculations for stfield star data

    tearDownClass method inherited without change from DbTestCase
    """

    # @classmethod
    # def setUpClass(cls):
    #     """Stuff to do once before running all class test methods."""

    #     super(StarFieldStarDataTests, cls).setUpClass()
    #     super(StarFieldStarDataTests, cls).load_test_data()
    #     cls.stf = SF_STF
    #     cls.stars = cls.stf.get_stars()
    #     cls.example_star = cls.stars[0]


    # def test_star_count(self):
    #     """Test the star count for the star field."""

    #     # we expect 55 stars for the test data set, San Francisco, TEST_DATETIME
    #     self.assertEqual(len(self.stars), 55)


    # def test_star_data_type(self):
    #     """Test the that the example star is a dict."""

    #     self.assertIsInstance(self.example_star, dict)


    # def test_star_keys(self):
    #     """Test the keys of the star dict of the first item in self.stars."""

    #     star_keys = set(self.example_star.keys())
    #     expected_keys = SKYOBJECT_KEY_SET
    #     self.assertEqual(star_keys, expected_keys)


    # def test_max_magnitude(self):
    #     """Test that no star's magnitude exceeds the maximum magnitude."""

    #     mags_over_max = [ star['magnitude'] for star in self.stars 
    #                       if star['magnitude'] > self.stf.max_mag ]

    #     self.assertEqual(mags_over_max, [])


class StarFieldConstellationDataTests(DbTestCase):
    """Test calculations for star and constellation data at a time and place.

    tearDownClass method inherited without change from DbTestCase
    """

    # @classmethod
    # def setUpClass(cls):
    #     """Stuff to do once before running all class test methods."""

    #     super(StarFieldConstellationDataTests, cls).setUpClass()
    #     super(StarFieldConstellationDataTests, cls).load_test_data()
    #     cls.ori = Constellation.query.filter_by(const_code='ORI').one()
    #     cls.tel = Constellation.query.filter_by(const_code='TEL').one()
    #     cls.expected_const_keys = set(['bound_verts', 'line_groups', 'code', 'name'])


    #########################################################
    # Constellation Line Groups
    #########################################################

    # def test_get_const_line_groups_types(self):
    #     """Make sure the function is returning data in the expected formats"""

    #     line_groups = SF_STF.get_const_line_groups(self.ori)

    #     example_group = line_groups[0]
    #     example_vertex = example_group[0]

    #     self.assertIsInstance(line_groups, list) 
    #     self.assertIsInstance(example_group, list) 
    #     self.assertIsInstance(example_vertex, dict) 
    #     self.assertEqual(set(example_vertex.keys()), COORDS_KEY_SET)


    # def const_line_groups_test(self, stf, const, expected_count):
    #     """Test constellation line groups for various inputs"
    #     """

    #     line_groups = stf.get_const_line_groups(const)
    #     self.assertEqual(len(line_groups), expected_count)


    # def test_const_line_groups_sf_ori(self):
    #     """Test constellation line groups for multi-group, visible"""

    #     self.const_line_groups_test(SF_STF, self.ori, expected_count=4)


    # def test_const_line_groups_sf_tel(self):
    #     """Test constellation line groups for single-group, not visible"""

    #     self.const_line_groups_test(SF_STF, self.tel, expected_count=1)


    # def test_const_line_groups_jo_ori(self):
    #     """Test constellation line groups for multi-group, not visible"""

    #     self.const_line_groups_test(J_STF, self.ori, expected_count=4)


    # def test_const_line_groups_jo_ori(self):
    #     """Test constellation line groups for single-group, visible"""

    #     self.const_line_groups_test(J_STF, self.tel, expected_count=1)


    #########################################################
    # Constellation Boundaries
    #########################################################

    # def test_get_const_bound_verts_types(self):
    #     """Make sure the function is returning data in the expected formats"""

    #     bound_verts = SF_STF.get_const_bound_verts(self.ori)

    #     example_vertex = bound_verts[0]

    #     self.assertIsInstance(bound_verts, list)
    #     self.assertIsInstance(example_vertex, dict) 
    #     self.assertEqual(set(example_vertex.keys()), COORDS_KEY_SET)


    # def const_bound_verts_test(self, stf, const, expected_count):
    #     """Generic test for constellation boundary data."""

    #     verts = stf.get_const_bound_verts(const)
    #     self.assertEqual(len(verts), expected_count)

    #     # check that th last vertex is a repeat of the first
    #     self.assertEqual(verts[0], verts[-1])


    # def test_sf_ori_bound_verts(self):
    #     """Test bound vertices for Orion. Starfield doesn't matter for this test
    #     """

    #     self.const_bound_verts_test(SF_STF, self.ori, 29)


    # def test_sf_tel_bound_verts(self):
    #     """Test bound vertices for Tel. Starfield doesn't matter for this test.
    #     """

    #     self.const_bound_verts_test(SF_STF, self.tel, 6)


    #########################################################
    # Constellation Data
    #########################################################

    # def test_get_const_data_types(self):
    #     """Make sure the function is returning data in the expected formats"""

    #     const_data = SF_STF.get_const_data(self.ori)

    #     example_bound_verts = const_data['bound_verts']
    #     example_bound_vertex = example_bound_verts[0]
    #     example_line_groups = const_data['line_groups']
    #     example_line_group = example_line_groups[0]
    #     example_line_vertex = example_line_group[0]

    #     self.assertIsInstance(const_data, dict) 
    #     self.assertEqual(set(const_data.keys()), self.expected_const_keys)

    #     self.assertIsInstance(example_bound_verts, list) 
    #     self.assertIsInstance(example_bound_vertex, dict) 
    #     self.assertEqual(set(example_bound_vertex.keys()), COORDS_KEY_SET)

    #     self.assertIsInstance(example_line_groups, list) 
    #     self.assertIsInstance(example_line_group, list) 
    #     self.assertIsInstance(example_line_vertex, dict) 
    #     self.assertEqual(set(example_line_vertex.keys()), COORDS_KEY_SET)


    # def get_const_data_test(self, stf, const, expected_type, expected_name):
    #     """Generic function for getting constellation data"""

    #     const_data = stf.get_const_data(const)

    #     self.assertIsInstance(const_data, expected_type)

    #     if expected_type == dict:
    #         self.assertEqual(const_data['name'], expected_name)


    # def test_get_const_sf_ori(self):
    #     """Test data returned for orion in sf."""

    #     self.get_const_data_test(SF_STF, self.ori, dict, 'Orion')


    # def test_get_const_sf_tel(self):
    #     """Test data returned for telescopium in sf."""

    #     self.get_const_data_test(SF_STF, self.tel, dict, 'Telescopium')


    # def test_get_const_johannesburg_ori(self):
    #     """Test data returned for orion in johannesburg."""

    #     self.get_const_data_test(J_STF, self.ori, dict, 'Orion')


    # def test_get_const_johannesburg_tel(self):
    #     """Test data returned for telescopium in johannesburg."""

    #     self.get_const_data_test(J_STF, self.tel, dict, 'Telescopium')


    #########################################################
    # Constellation List
    #########################################################

    # def test_get_consts_types(self):
    #     """Make sure the function is returning data in the expected formats"""

    #     consts = SF_STF.get_consts()
    #     example_const = consts[0]

    #     self.assertIsInstance(consts, list) 
    #     self.assertIsInstance(example_const, dict) 
    #     self.assertEqual(set(example_const.keys()), self.expected_const_keys)


    # def const_list_test(self, stf):
    #     """Generic test for returning constellation list. 

    #     Output should be the same regardless of starfield constraints."""

    #     consts = stf.get_consts()

    #     # get the list of names with a set comprehension
    #     const_names = set(const['name'] for const in consts)

    #     self.assertEqual(len(consts), 3)
    #     self.assertEqual(const_names, CONST_LIST_SET)


    # def test_sf_consts(self):
    #     """Test data returned for constellations in SF."""

    #     self.const_list_test(SF_STF)


    # def test_johannesburg_consts(self):
    #     """Test data returned for constellations in Johannesburg."""

    #     self.const_list_test(J_STF)

