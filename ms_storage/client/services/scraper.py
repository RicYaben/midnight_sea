from ms_storage.client.interfaces import ExService, Scraper, ServiceFactory
from ms_storage.protos.scraper_pb2 import ScrapeRequest
from ms_storage.protos.scraper_pb2_grpc import ScraperStub

from google.protobuf import json_format


@ServiceFactory.register("scraper")
class ScraperService(ExService, Scraper):
    _stub_class = ScraperStub

    def scrape(self, model: str, market: str, data: bytes):
        request = ScrapeRequest(model=model.value, market=market, data=data)
        response = self.stub.Scrape(request)

        ret = json_format.MessageToDict(response.content)
        return ret
