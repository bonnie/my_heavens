"""Tests for the database code"""

from unittest import TestCase

# be able to import from parent dir
import sys
sys.path.append('..')

from server import app
from model import connect_to_db, db
# from tests import TESTDATA_DIR, TESTDB_URI


class DbTests(TestCase):
    """Test retrieving data from the database."""


