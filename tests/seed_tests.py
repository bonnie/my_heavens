"""Tests for the seeding code."""

from unittest import TestCase

# be able to import from parent dir
import sys
sys.path.append('..')

import seed
from server import app
from model import connect_to_db, db
from run_tests import TESTDB_URI, TESTDATA_DIR

class SeedTests(TestCase):
    """Test the code to seed the database."""

    def SetUp(self):
        """Stuff to do before every test."""

        connect_to_db(app, TESTDB_URI)
        db.create_all()

    def TearDown(self):
        """Stuff to do after every test."""

        db.session.close()
        db.drop_all()

    def test_open_datafile(self):
        """Test the function that locates and opens the file."""

        f = seed.open_datafile(TESTDATA_DIR, 'stars')
        first_line_tokens = f.readline().split(',')

        # check that it's a csv with the appropriate number of columns
        self.assertEqual(len(first_line_tokens), 14)

