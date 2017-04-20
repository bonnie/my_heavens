"""Tests for the seeding code.

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
import os

# be able to import from parent dir
import sys
sys.path.append('..')

from run_tests import TESTDATA_DIR, DbTestCase

# don't init the tzwhere variable; it takes a lot of time and it's not necessary
# here
os.environ['TZW_INIT'] = "False"

from model import db, Constellation, Star, BoundVertex, \
                  ConstBoundVertex, ConstLineGroup, ConstLineVertex
import seed

class SeedTestsWithoutDb(TestCase):
    """Test the 'helper' functions that don't need the database."""

    def test_get_degrees_from_hours_and_invert_pos(self):
        """Test translation of RA in hours to inverted degrees for positive RA"""

        deg = seed.get_degrees_from_hours_and_invert(6)
        self.assertEqual(deg, 270)

    def test_get_degrees_from_hours_and_invert_zero(self):
        """Test translation of RA in hours to inverted degrees for zero RA"""

        deg = seed.get_degrees_from_hours_and_invert(0)
        self.assertEqual(deg, 360)

    def test_open_datafile(self):
        """Test the function that locates and opens the file."""

        f = seed.open_datafile(TESTDATA_DIR, 'stars')
        first_line_tokens = f.readline().split(',')

        # check that it's a csv with the appropriate number of columns
        self.assertEqual(len(first_line_tokens), 14)

    def test_get_color_fullyknown(self):
        """Test getting a color for a known spectral class."""

        color = seed.get_color('B2III SB    ')
        self.assertEqual(color, '#9fb4ff')

    def test_get_color_letterknown(self):
        """Test getting a color for a spectral class only whose letter is known."""

        color = seed.get_color('O9.5II      ')

        # the color is chosen randomly from the possible O9 colors
        O9_colors = ['#9bb0ff', '#a4b9ff', '#9eb1ff', '#a4baff']
        self.assertIn(color, O9_colors)

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
        """Test extracting the name and constellation for stars with out an explicit name.""" 

        star_info = {'ProperName': ' ',
                     'BayerFlamsteed': ' 70Xi  Ori'}

        name, const = seed.get_name_and_constellation(star_info)
        self.assertEqual(name, 'Xi Ori')
        self.assertEqual(const, 'ORI')

    def test_get_name_and_constellation_bfname_no_leading_number(self):
        """Test extracting the name and constellation for stars without an explicit name; BF data has no leading number.""" 

        star_info = {'ProperName': ' ',
                     'BayerFlamsteed': '   Del2Tel'}

        name, const = seed.get_name_and_constellation(star_info)
        self.assertEqual(name, 'Del2Tel')
        self.assertEqual(const, 'TEL')

    def test_get_name_and_constellation_noname(self):
        """Test extracting the name and constellation for stars without an explicit name.""" 

        star_info = {'ProperName': ' ',
                     'BayerFlamsteed': ' 74    Ori'}

        name, const = seed.get_name_and_constellation(star_info)
        self.assertEqual(name, None)
        self.assertEqual(const, 'ORI')        


class SeedTestsWithDb(DbTestCase):
    """Test the code that actually seeds the db.

    setUpClass and tearDownClass methods inherited without change from 
    dbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(SeedTestsWithDb, cls).setUpClass()

        # a bounds vertex for orion
        cls.bv_ra = 271.750
        cls.bv_dec = 21.500

    def test_get_bounds_vertex_not_exists(self):
        """Test code to detect an existing constellation bounds vertex."""

        new_vertex = seed.get_bounds_vertex(self.bv_ra, self.bv_dec)
        self.assertIsInstance(new_vertex, BoundVertex)        

    def test_get_bounds_vertex_exists(self):
        """Test code to detect an existing constellation bounds vertex."""

        # create the vertex in the db
        vertex = BoundVertex(ra=self.bv_ra, dec=self.bv_dec)
        db.session.add(vertex)
        db.session.commit

        matched_vertex = seed.get_bounds_vertex(self.bv_ra, self.bv_dec)
        self.assertIsInstance(matched_vertex, BoundVertex)


class SeedConstellationTests(DbTestCase):
    """Test code to loading constellations and constellation boundaries into the database.

    tearDownClass method inherited without change from DbTestCase"""

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(SeedConstellationTests, cls).setUpClass()
        seed.load_constellations(TESTDATA_DIR)

    def test_load_constellations(self):
        """Test code to load constellations into db."""

        # see how many constellations got added
        self.assertEqual(Constellation.query.count(), 3)

        # see whether the info made it into the right columns
        orion = Constellation.query.filter_by(const_code='ORI').one()
        self.assertEqual(orion.const_code, 'ORI')
        self.assertEqual(orion.name, 'Orion')

    def test_load_const_boundaries(self):
        """Test code to load the constellation boundaries into the database."""

        # then load the boundaries
        seed.load_const_boundaries(TESTDATA_DIR)

        # how does it look? 
        ori_count = ConstBoundVertex.query.filter_by(const_code = 'ORI').count()
        self.assertEqual(ori_count, 28)


class SeedStarTests(DbTestCase):
    """Test seeding stars into the database.

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(SeedStarTests, cls).setUpClass()
        seed.load_constellations(TESTDATA_DIR)
        seed.load_stars(TESTDATA_DIR)

    def test_star_data(self):
        """Test code to load stars into the databse."""

        rigel = Star.query.filter_by(name='Rigel').one()
        self.assertEqual(rigel.const_code, 'ORI')
        self.assertEqual(float(rigel.distance), 236.97)
        self.assertEqual(float(rigel.magnitude), 0.18)
        self.assertEqual(rigel.spectrum, 'B8Ia')
        self.assertEqual(rigel.color, '#b6ceff')

    def test_degree_range(self):
        """Make sure all the ra and decs in the db are in degree range."""

        ra_outofrange_count = Star.query.filter(db.not_(db.between(Star.ra, 0, 360))).count()
        dec_outofrange_count = Star.query.filter(db.not_(db.between(Star.dec, -90, 90))).count()

        self.assertEqual(ra_outofrange_count, 0)
        self.assertEqual(dec_outofrange_count, 0)


    def matching_star_test(self, ra, dec, mag, name):
        """Test for matching stars from constellation lines data.

        This is a generic test so that the following tests have less repeated
        code.
        """

        ra_in_deg = seed.get_degrees_from_hours_and_invert(ra)
        star = seed.get_matching_star(ra_in_deg, dec, mag)

        self.assertIsInstance(star, Star)
        self.assertEqual(star.name, name)


    def test_get_matching_star_exact_match(self):
        """Test finding a matching star by RA, dec, mag"""

        # Betelgeuse (Alpha Ori)
        ra = 5.919444
        dec = 7.4000
        mag = 0.80

        self.matching_star_test(ra, dec, mag, 'Betelgeuse')

    def test_get_matching_star_no_mag(self):
        """Test finding a matching star by RA, dec when there's no mag match"""

        # Beta Mon
        ra = 6.480278
        dec = -7.0333
        mag = 4.60

        self.matching_star_test(ra, dec, mag, 'Bet Mon')

    def test_get_matching_star_brightest(self):
        """Test finding a matching star by RA, dec when there's more than one match"""

        # Delta Tel (1)
        ra = 18.529167
        dec = -45.9167
        mag = 4.95

        self.matching_star_test(ra, dec, mag, 'Del1Tel')


class SeedConstLineTests(DbTestCase):
    """Test seeding constellation lines into the database.

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(SeedConstLineTests, cls).setUpClass()
        seed.load_constellations(TESTDATA_DIR)
        seed.load_stars(TESTDATA_DIR)
        seed.load_constellation_lines(TESTDATA_DIR)


    def test_const_line_group_count(self):
        """Test that the appropriate number of line groups were added to db."""

        ori_group_count = ConstLineGroup.query.filter_by(const_code='ORI').count()
        self.assertEqual(ori_group_count, 4)


    def test_const_line_vertex_count(self):
        """Test that the appropriate number of line vertices were added to db."""

        vertex_query = db.session.query(ConstLineVertex)
        ori_vertex_query = vertex_query.filter(ConstLineGroup.const_code=='ORI')
        ori_vertex_join = ori_vertex_query.join(ConstLineGroup)
        ori_vertex_count = ori_vertex_join.count()
        self.assertEqual(ori_vertex_count, 25)
