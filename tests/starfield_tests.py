"""Tests for the Starfield code."""

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
from run_tests import SF_LAT, SF_LNG, SF_STF, J_LAT, J_LNG, J_STF, TEST_DATETIME

# acceptable margin when comparing floats
MARGIN = 0.005

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
    # lat/lng string tests
    #########################################################

    def test_sf_lat(self):
        """Test sf latitude string."""

        lstring = SF_STF.get_lat_or_lng_string('lat')
        self.assertEqual(lstring, '37.77&deg; N')

    def test_sf_lon(self):
        """Test sf longitude string."""

        lstring = SF_STF.get_lat_or_lng_string('lon')
        self.assertEqual(lstring, '122.42&deg; W')

    def test_johannesburg_lat(self):
        """Test johannesburg latitude string."""

        lstring = J_STF.get_lat_or_lng_string('lat')
        self.assertEqual(lstring, '26.20&deg; S')

    def test_johannesburg_lon(self):
        """Test johannesburg longitude string."""

        lstring = J_STF.get_lat_or_lng_string('lon')
        self.assertEqual(lstring, '28.05&deg; E')


    #########################################################
    # starfield spec tests
    #########################################################

    def test_starfield_spec_format(self):
        """Test the format of the dict returned by the starfield spec generator."""

        spec_keys = set(['lat', 'lng', 'dateString', 'timeString'])
        specs = SF_STF.get_specs()

        self.assertEqual(set(specs.keys()), spec_keys)
        self.assertIsInstance(specs['lat'], str)
        self.assertIsInstance(specs['lng'], str)
        self.assertIsInstance(specs['dateString'], str)
        self.assertIsInstance(specs['timeString'], str)

    def test_sf_specs(self):
        """Test specs returned for SF test starfield."""

        specs = SF_STF.get_specs()
        self.assertEqual(specs['lat'], '37.77&deg; N')
        self.assertEqual(specs['lng'], '122.42&deg; W')
        self.assertEqual(specs['dateString'], 'March 1, 2017')
        self.assertEqual(specs['timeString'], '9:00 PM')

    def test_johannesburg_specs(self):
        """Test specs returned for Johannesburg test starfield."""

        specs = J_STF.get_specs()
        self.assertEqual(specs['lat'], '26.20&deg; S')
        self.assertEqual(specs['lng'], '28.05&deg; E')
        self.assertEqual(specs['dateString'], 'March 1, 2017')
        self.assertEqual(specs['timeString'], '9:00 PM')

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
    # get local time from ephem time
    #########################################################

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
    # get rise and set times
    #########################################################

    def get_rise_set_times_test(self, stf, obj, expected_rise, expected_set):
        """Generic test to get the rise / set times."""

        trise, tset = stf.get_rise_set_times(obj(stf.ephem))
        self.assertEqual(trise, expected_rise)
        self.assertEqual(tset, expected_set)

    def test_sf_moon_riseset(self):
        """Test rise and set times for moon for sf starfield."""

        trise = '8:40 AM'
        tset = '9:43 PM'

        self.get_rise_set_times_test(SF_STF, ephem.Moon, trise, tset)

    def test_johannesburg_moon_riseset(self):
        """Test rise and set times for moon for johannesburg starfield."""

        trise = '8:37 AM'
        tset = '9:30 PM'

        self.get_rise_set_times_test(J_STF, ephem.Moon, trise, tset)

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

        # how much 'slop' we'll allow before deciding it's the wrong answer
        margin = 0.0001

        self.assertWithinMargin(pdata['ra'], expected_ra, margin)
        self.assertWithinMargin(pdata['dec'], expected_dec, margin)

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

    def moon_data_test(self, stf, ra, dec, phase, colong, rotation, trise, tset):
        """Generic test for moon data."""

        mdata = SF_STF.get_moon()
        self.assertEqual(mdata['ra'], ra)
        self.assertEqual(mdata['dec'], dec)
        self.assertEqual(mdata['phase'], phase)
        self.assertEqual(mdata['colong'], colong)
        self.assertEqual(mdata['rotation'], rotation)
        self.assertEqual(mdata['prevRise'], trise)
        self.assertEqual(mdata['nextSet'], tset)

    def test_sf_moon_data(self):
        """Test moon data for San Francisco."""

        # expected data
        ra = 332.8583815004972
        dec = 6.260453993509564
        phase = 'waxing crescent: 16.1'
        colong = 318.9918500407805
        rotation = 383.33266920101795
        trise = '8:40 AM'
        tset = '9:43 PM'

        self.moon_data_test(SF_STF, ra, dec, phase, colong, rotation, trise, tset)

    def test_johannesburg_moon_data(self):
        """Test moon data for Johannesburg"""

        # expected data
        ra = 332.8583815004972
        dec = 6.260453993509564
        phase = 'waxing crescent: 16.1'
        colong = 318.9918500407805
        rotation = 383.33266920101795
        trise = '8:40 AM'
        tset = '9:43 PM'

        self.moon_data_test(J_STF, ra, dec, phase, colong, rotation, trise, tset)

    #########################################################
    # moon phase phrase tests
    #########################################################

    def phase_phrase_test(self, sf_datetime, expected_phrase):
        """Generic test for testing moon phase phrase."""

        sf_timestring = datetime.strftime(sf_datetime, BOOTSTRAP_DTIME_FORMAT)
        stf = StarField(lat=SF_LAT, lng=SF_LNG, localtime_string=sf_timestring)
        growth, phase_phrase = stf.get_moon_phase_phrase()
        self.assertEqual(phase_phrase, expected_phrase)

    def test_waxing_crescent(self):
        """Test moon phase phrase for waxing crescent."""

        sf_datetime = datetime(2017, 3, 1, 21, 0, 0)
        phrase = 'waxing crescent: 15.8'
        self.phase_phrase_test(sf_datetime, phrase)

    def test_waning_crescent(self):
        """Test moon phase phrase for waning crescent."""

        sf_datetime = datetime(2017, 2, 25, 21, 0, 0)
        phrase = 'waning crescent: 0.2'
        self.phase_phrase_test(sf_datetime, phrase)

    def test_waxing_gibbous(self):
        """Test moon phase phrase for waxing gibbous."""

        sf_datetime = datetime(2017, 2, 5, 21, 0, 0)
        phrase = 'waxing gibbous: 72.6'
        self.phase_phrase_test(sf_datetime, phrase)

    def test_waning_gibbous(self):
        """Test moon phase phrase for waning gibbous."""

        sf_datetime = datetime(2017, 2, 15, 21, 0, 0)
        phrase = 'waning gibbous: 73.9'
        self.phase_phrase_test(sf_datetime, phrase)

    def test_first_quarter(self):
        """Test moon phase phrase for first quarter."""

        sf_datetime = datetime(2017, 2, 3, 20, 0, 0)
        phrase = 'first quarter'
        self.phase_phrase_test(sf_datetime, phrase)

    def test_third_quarter(self):
        """Test moon phase phrase for third quarter."""

        sf_datetime = datetime(2017, 2, 18, 12, 0, 0)
        phrase = 'third quarter'
        self.phase_phrase_test(sf_datetime, phrase)

    def test_full_moon(self):
        """Test moon phase phrase for full moon."""

        sf_datetime = datetime(2017, 2, 10, 20, 0, 0)
        phrase = 'full moon'
        self.phase_phrase_test(sf_datetime, phrase)

    def test_new_moon(self):
        """Test moon phase phrase for new moon."""

        sf_datetime = datetime(2017, 2, 26, 10, 0, 0)
        phrase = 'new moon'
        self.phase_phrase_test(sf_datetime, phrase)

    #########################################################
    # moon rotation tests
    #########################################################

    def moon_rotation_test(self, stf, expected_rotation):
        """Generic test for moon rotation."""

        growth, phase_phrase = stf.get_moon_phase_phrase()
        rotation = stf.calculate_moon_angle(growth)
        self.assertWithinMargin(rotation, expected_rotation, 0.00001)

    def waning_moon_rotation_test(self, lat, lng, expected_rotation):
        """Generic test for a waning datetime.

        (different from standard test datetime for this file)"""

        wan_datetime = datetime(2017, 2, 15, 21, 0, 0)
        wan_timestring = datetime.strftime(wan_datetime, BOOTSTRAP_DTIME_FORMAT)
        stf = StarField(lat=lat, lng=lng, localtime_string=wan_timestring)
        self.moon_rotation_test(stf, expected_rotation)

    def test_sf_waxing_moon_rotation(self):
        """Test rotation of moon for sf when moon is waxing."""

        self.moon_rotation_test(SF_STF, 383.33266920101795)

    def test_johannesburg_waxing_moon_rotation(self):
        """Test rotation of moon for johannesburg when moon is waxing."""

        self.moon_rotation_test(J_STF, 321.4308005282016)

    def test_sf_waning_moon_rotation(self):
        """Test rotation of moon for sf when moon is waning."""

        self.waning_moon_rotation_test(SF_LAT, SF_LNG, -26.004438784074594)

    def test_johannesburg_waning_moon_rotation(self):
        """Test rotation of moon for johannesburg when moon is waning."""

        self.waning_moon_rotation_test(J_LAT, J_LNG, 57.972361308833435)

    #########################################################
    # sky rotation tests
    #########################################################

    def test_sky_rotation_format(self):
        """Test the format of the sky rotation output."""

        sky_rotation = SF_STF.get_sky_rotation()
        self.assertIsInstance(sky_rotation, dict)
        self.assertEqual(set(sky_rotation.keys()), set(['lambda', 'phi']))
        self.assertIsInstance(sky_rotation['lambda'], float)
        self.assertIsInstance(sky_rotation['phi'], float)

    def sky_rotation_test(self, stf, expected_lambda, expected_phi):
        """Generic test for sky rotation."""

        sky_rotation = stf.get_sky_rotation()
        self.assertWithinMargin(sky_rotation['lambda'], expected_lambda, 0.00001)
        self.assertWithinMargin(sky_rotation['phi'], expected_phi, 0.00001)

    def test_sf_sky_rotation(self):
        """Test sky rotation for san francisco starfield."""

        self.sky_rotation_test(SF_STF, 112.76234354938829, 0 - SF_LAT)

    def test_johannesburg_sky_rotation(self):
        """Test sky rotation for johannesburg starfield."""

        self.sky_rotation_test(J_STF, 112.81837654938823, 0 - J_LAT)
   