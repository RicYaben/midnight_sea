from ms_scraper.protos import scraper_pb2, scraper_pb2_grpc
from ms_scraper.scraper.scraper import scrape
from ms_scraper.server.interfaces import Service, ServiceFactory
from google.protobuf.struct_pb2 import Struct


@ServiceFactory.register("Scraper")
class Scraper(scraper_pb2_grpc.ScraperServicer, Service):
    """Endpoint for the Scraper functions"""

    def Scrape(self, request, context) -> scraper_pb2.ScrapeResponse:
        """Returns the content scraped from an HTML page"""

        # scrape the content from the data
        content = scrape(market=request.market, model=request.model, html=request.data)

        content_struct = Struct()
        content_struct.update(content)

        response = scraper_pb2.ScrapeResponse(content=content_struct)

        return response
