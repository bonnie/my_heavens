"""Tests for the seeding code."""

from unittest import TestCase

# be able to import from parent dir
import sys
sys.path.append('..')

import seed
from server import app
from model import connect_to_db, db
from run_tests import TESTDB_URI, TESTDATA_DIR

def is_within_tolerance(num, target):
    """Check to see whether a num is within a reasonable tolerance of target. 

    This is used to account for float discrepancies based on storage vagaries.
    """
    tolerance = 0.0001
    return abs(num - target) <= tolerance


class SeedTestsWithoutDb(TestCase):
    """Test the 'helper' functions that don't need the database."""

    def test_open_datafile(self):
        """Test the function that locates and opens the file."""

        f = seed.open_datafile(TESTDATA_DIR, 'stars')
        first_line_tokens = f.readline().split(',')

        # check that it's a csv with the appropriate number of columns
        self.assertEqual(len(first_line_tokens), 14)


    def test_get_radian_coords_decimal(self):
        """Test getting radian coords from ra in hours and dec in degrees N."""

        # betelgeuse
        ra_in_hours = "5.91952477"
        dec_in_degrees = "+07.40703634"
        # dec_in_degrees = str(07 + 24/60.0 + 25.4304/3600) + 'dN'

        ra_in_rad, dec_in_rad = seed.get_radian_coords(ra_in_hours, dec_in_degrees)
        self.assertTrue(is_within_tolerance(ra_in_rad, 1.5497291380724814))
        self.assertTrue(is_within_tolerance(dec_in_rad, 0.12927765470594127))


    def test_get_radian_coords_S(self):
        """Test getting radian coords from ra in hours and dec in degrees S."""

        # antares
        ra_in_hours = "16.49012986"
        dec_in_degrees = "-26.43194608"

        # dec_in_degrees = str(26 + 25/60.0 + 55.2094/3600) + 'dS'

        ra_in_rad, dec_in_rad = seed.get_radian_coords(ra_in_hours, dec_in_degrees)
        self.assertTrue(is_within_tolerance(ra_in_rad, 4.317105335135356))
        self.assertTrue(is_within_tolerance(dec_in_rad, -0.46132547345962727))


    def test_get_color_fullyknown(self):
        """Test getting a color for a known spectral class."""

        color = seed.get_color('B2III SB    ')
        self.assertEqual(color, '#9fb4ff')


    def test_get_color_letterknown(self):
        """Test getting a color for a spectral class only whose letter is known."""

        color = seed.get_color('O9.5II      ')

        # the color is chosen randomly from the possible 09 colors
        self.assertIn(color, ['#9bb0ff', '#a4b9ff', '#9eb1ff', '#a4baff'])


    def test_get_color_unknown(self):
        """Test getting a color for a spectral class only whose letter is known."""

        color = seed.get_color('Am...       ')
        self.assertEqual(color, '#ffffff')


    def test_get_name_and_constellation_name(self):
        """Test extracting the name and constellation for stars with an explicit name.""" 

        star_info = {'ProperName': 'Antares',
                     'BayerFlamsteed': ' 21Alp Sco'}

        name, const = seed.get_name_and_constellation(star_info)
        self.assertEqual(name, 'Antares')
        self.assertEqual(const, 'SCO')


    def test_get_name_and_constellation_bfname(self):
        """Test extracting the name and constellation for stars with an explicit name.""" 

        star_info = {'ProperName': ' ',
                     'BayerFlamsteed': ' 70Xi  Ori'}

        name, const = seed.get_name_and_constellation(star_info)
        self.assertEqual(name, 'Xi Ori')
        self.assertEqual(const, 'ORI')


    def test_get_name_and_constellation_noname(self):
        """Test extracting the name and constellation for stars without an explicit name.""" 

        star_info = {'ProperName': ' ',
                     'BayerFlamsteed': ' 74    Ori'}

        name, const = seed.get_name_and_constellation(star_info)
        self.assertEqual(name, None)
        self.assertEqual(const, 'ORI')        


class SeedTestsWithDb(TestCase):
    """Test the code that actually seeds the db."""

    def SetUp(self):
        """Stuff to do before every test."""

        connect_to_db(app, TESTDB_URI)
        db.create_all()


    def TearDown(self):
        """Stuff to do after every test."""

        db.session.close()
        db.drop_all()



