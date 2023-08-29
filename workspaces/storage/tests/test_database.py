

import unittest
from storage.database.database import Database

class TestDatabase(unittest.TestCase):

    def test_load_db(self):
        db = Database()

        self.assertIsInstance(db, Database)