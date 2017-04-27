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
CONST_LIST_SET = set(['Orion', 'Monoceros', 'Telescopium', 'Serpens', 'Ophiuchus'])

# Rigel
R_RA = 1.372
R_DEC = -0.143

# Alpha Tel
AT_RA = 4.851
AT_DEC = -0.801

class StarDataTests(DbTestCase):
    """Test calculations for star data

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

        # we expect 55 stars for the test data set
        self.assertEqual(len(self.stars), 111)

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
    """Test calculations of constellation data.

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(ConstellationDataTests, cls).setUpClass()
        super(ConstellationDataTests, cls).load_test_data()
        cls.ori = Constellation.query.get('ORI')
        cls.tel = Constellation.query.get('TEL')

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

    def test_ori_bound_verts(self):
        """Test bound vertices for Orion."""

        self.const_bound_verts_test(self.ori, 29)

    def test_tel_bound_verts(self):
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

        self.assertEqual(len(consts), 5)
        self.assertEqual(const_names, CONST_LIST_SET)

class SerpensConstellationDataTests(DbTestCase):
    """Test calculations for the problem child constellation: Serpens.

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(SerpensConstellationDataTests, cls).setUpClass()
        super(SerpensConstellationDataTests, cls).load_test_data()
        consts = get_constellations()
        for const in consts:
            if const['code'] == 'SER':
                cls.serpens_data = const
                break

    def test_serpens_bound_verts_two_areas(self):
        """Test bound vertices for our problem child."""

        bound_verts = self.serpens_data['bound_verts']
        self.assertEqual(len(bound_verts), 2)

    def test_serpens_first_bound_verts_length(self):
        """Test the length of the first bound verts group."""

        bvset1 = self.serpens_data['bound_verts'][0]
        self.assertEqual(len(bvset1), 16)

    def test_serpens_first_bound_verts_length(self):
        """Test the length of the second bound verts group."""

        bvset2 = self.serpens_data['bound_verts'][1]
        self.assertEqual(len(bvset2), 26)

    def test_serpens_bound_vert_format(self):
        """Test that the first bound vertex is a two item list."""

        vertex = self.serpens_data['bound_verts'][0][0]
        self.assertEqual(len(vertex), 2)

    def test_serpens_line_groups_length(self):
        """Test the length of the line groups list."""

        linegroups = self.serpens_data['line_groups']
        self.assertEqual(len(linegroups), 1)

    def test_serpens_line_group_length(self):
        """Test the length of the line group list."""

        line_group = self.serpens_data['line_groups'][0]
        self.assertEqual(len(line_group), 18)

    def test_serpens_line_vertex_format(self):
        """Test that the first line vertex is a two item list."""

        line_vertex = self.serpens_data['line_groups'][0][0]
        self.assertEqual(len(line_vertex), 2)
