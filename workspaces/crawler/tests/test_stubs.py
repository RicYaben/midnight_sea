# Import all the services
import unittest

from crawler.stubs.storage import LocalStorageService
from lib.config.config import Client
from lib.stubs.factory import StubFactory


class TestStubs(unittest.TestCase):

    def test_load_stub(self):
        client: Client = Client(
            address="localhost",
            port=0,
            name="storage",
            local=True
        ) 
        storage = StubFactory.create_stub(client)

        self.assertIsInstance(storage, LocalStorageService)