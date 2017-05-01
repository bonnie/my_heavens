"""Tests for model repr methods."""

    # Copyright (c) 2017 Bonnie Schulkin

    # This file is part of My Heavens.

    # My Heavens is free software: you can redistribute it and/or modify it
    # under the terms of the GNU Affero General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or (at your
    # option) any later version.

    # My Heavens is distributed in the hope that it will be useful, but WITHOUT
    # ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    # FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
    # License for more details.

    # You should have received a copy of the GNU Affero General Public License
    # along with My Heavens. If not, see <http://www.gnu.org/licenses/>.

from unittest import TestCase

# be able to import from parent dir
import sys
sys.path.append('..')

from run_tests import TESTDATA_DIR, DbTestCase
from model import db, Constellation, Star, BoundVertex, \
                  ConstBoundVertex, ConstLineGroup, ConstLineVertex


class ModelReprTests(DbTestCase):
    """Test model repr functions.

    tearDownClass method inherited without change from DbTestCase
    """

    @classmethod
    def setUpClass(cls):
        """Stuff to do once before running all class test methods."""

        super(ModelReprTests, cls).setUpClass()
        super(ModelReprTests, cls).load_test_data() 


    def test_star_repr(self):
        """Test repr method for Star class."""

        star = Star.query.first()
        self.assertIsInstance(repr(star), str)

    def test_constellation_repr(self):
        """Test repr method for Constellation class."""

        const = Constellation.query.first()
        self.assertIsInstance(repr(const), str)

    def test_boundvertex_repr(self):
        """Test repr method for BoundVertex class."""

        bv = BoundVertex.query.first()
        self.assertIsInstance(repr(bv), str)

    def test_constboundvertex_repr(self):
        """Test repr method for ConstBoundVertex class."""

        cbv = ConstBoundVertex.query.first()
        self.assertIsInstance(repr(cbv), str)

    def test_constlinegroup_repr(self):
        """Test repr method for constlinegroup class."""

        clg = ConstLineGroup.query.first()
        self.assertIsInstance(repr(clg), str)

    def test_constlinevertex_repr(self):
        """Test repr method for ConstLineVertex class."""

        clv = ConstLineVertex.query.first()
        self.assertIsInstance(repr(clv), str)

