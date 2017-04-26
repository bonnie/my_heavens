"""Tests for the stars and constellations calculations code."""

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

from run_tests import DbTestCase, MAX_MAG, COORDS_KEY_SET, SKYOBJECT_KEY_SET
from stars import get_stars, get_const_line_groups, get_const_bound_verts, \
    get_const_data, get_constellations
from model import Constellation

# expected star dict keys
STAR_KEY_SET = SKYOBJECT_KEY_SET | set(['specClass', 'absMagnitude'])

# expected constellation keys
CONST_KEY_SET = set(['bound_verts', 'line_groups', 'code', 'name'])

# expected constellations
CONST_LIST_SET = set(['Orion', 'Monoceros', 'Telescopium'])

# Rigel
R_RA = 1.372
R_DEC = -0.143

# Alpha Tel
AT_RA = 4.851
AT_DEC = -0.801

class StarDataTests(DbTestCase):
    """Test calculations for stfield star data

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(StarDataTests, cls).setUpClass()
        super(StarDataTests, cls).load_test_data()
        cls.stars = get_stars(MAX_MAG)
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
        expected_keys = STAR_KEY_SET
        self.assertEqual(star_keys, expected_keys)

    def test_max_magnitude(self):
        """Test that no star's magnitude exceeds the maximum magnitude."""

        mags_over_max = [ star['magnitude'] for star in self.stars 
                          if star['magnitude'] > MAX_MAG ]

        self.assertEqual(mags_over_max, [])


class ConstellationDataTests(DbTestCase):
    """Test calculations for star and constellation data at a time and place.

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(ConstellationDataTests, cls).setUpClass()
        super(ConstellationDataTests, cls).load_test_data()
        cls.ori = Constellation.query.filter_by(const_code='ORI').one()
        cls.tel = Constellation.query.filter_by(const_code='TEL').one()

    #########################################################
    # Constellation Line Groups
    #########################################################

    def test_get_const_line_groups_types(self):
        """Make sure the function is returning data in the expected formats"""

        line_groups = get_const_line_groups(self.ori)

        example_group = line_groups[0]
        example_vertex = example_group[0]

        self.assertIsInstance(line_groups, list) 
        self.assertIsInstance(example_group, list) 
        self.assertIsInstance(example_vertex, list) 
        self.assertEqual(len(example_vertex), 2)

    def const_line_groups_test(self, const, expected_count):
        """Test constellation line groups for various inputs"
        """

        line_groups = get_const_line_groups(const)
        self.assertEqual(len(line_groups), expected_count)

    def test_const_line_groups_sf_ori(self):
        """Test constellation line groups for multi-group"""

        self.const_line_groups_test(self.ori, expected_count=4)

    def test_const_line_groups_jo_ori(self):
        """Test constellation line groups for single-group"""

        self.const_line_groups_test(self.tel, expected_count=1)


    #########################################################
    # Constellation Boundaries
    #########################################################

    def test_get_const_bound_verts_types(self):
        """Make sure the function is returning data in the expected formats"""

        bound_verts = get_const_bound_verts(self.ori)

        example_vertex = bound_verts[0][0]

        self.assertIsInstance(bound_verts, list)
        self.assertIsInstance(example_vertex, list)
        self.assertEqual(len(example_vertex), 2)

    def const_bound_verts_test(self, const, expected_count):
        """Generic test for constellation boundary data."""

        verts = get_const_bound_verts(const)[0]
        self.assertEqual(len(verts), expected_count)

        # check that th last vertex is a repeat of the first
        self.assertEqual(verts[0], verts[-1])

    def test_sf_ori_bound_verts(self):
        """Test bound vertices for Orion."""

        self.const_bound_verts_test(self.ori, 29)

    def test_sf_tel_bound_verts(self):
        """Test bound vertices for Tel."""

        self.const_bound_verts_test(self.tel, 6)


    #########################################################
    # Constellation Data
    #########################################################

    def test_get_const_data_types(self):
        """Make sure the function is returning data in the expected formats"""

        const_data = get_const_data(self.ori)

        example_bound_verts = const_data['bound_verts'][0]
        example_bound_vertex = example_bound_verts[0]
        example_line_groups = const_data['line_groups']
        example_line_group = example_line_groups[0]
        example_line_vertex = example_line_group[0]

        self.assertIsInstance(const_data, dict) 
        self.assertEqual(set(const_data.keys()), CONST_KEY_SET)

        self.assertIsInstance(example_bound_verts, list) 
        self.assertIsInstance(example_bound_vertex, list) 
        self.assertEqual(len(example_bound_vertex), 2)

        self.assertIsInstance(example_line_groups, list) 
        self.assertIsInstance(example_line_group, list) 
        self.assertIsInstance(example_line_vertex, list) 
        self.assertEqual(len(example_line_vertex), 2)


    def get_const_data_test(self, const, expected_type, expected_name):
        """Generic function for getting constellation data"""

        const_data = get_const_data(const)

        self.assertIsInstance(const_data, expected_type)

        if expected_type == dict:
            self.assertEqual(const_data['name'], expected_name)

    def test_get_const_sf_ori(self):
        """Test data returned for orion."""

        self.get_const_data_test(self.ori, dict, 'Orion')

    def test_get_const_sf_tel(self):
        """Test data returned for telescopium."""

        self.get_const_data_test(self.tel, dict, 'Telescopium')


    #########################################################
    # Constellation List
    #########################################################

    def test_get_consts_types(self):
        """Make sure the function is returning data in the expected formats"""

        consts = get_constellations()
        example_const = consts[0]

        self.assertIsInstance(consts, list) 
        self.assertIsInstance(example_const, dict) 
        self.assertEqual(set(example_const.keys()), CONST_KEY_SET)

    def test_const_list(self):
        """Test list of returned constellations."""

        consts = get_constellations()

        # get the list of names with a set comprehension
        const_names = set(const['name'] for const in consts)

        self.assertEqual(len(consts), 3)
        self.assertEqual(const_names, CONST_LIST_SET)
