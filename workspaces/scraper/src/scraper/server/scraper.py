# Copyright 2023 Ricardo Yaben
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from lib.protos import scraper_pb2, scraper_pb2_grpc
from scraper.scraper.scraper import scrape
from google.protobuf.struct_pb2 import Struct


class Scraper(scraper_pb2_grpc.ScraperServicer):
    """Endpoint for the Scraper functions"""

    def Scrape(self, request, context) -> scraper_pb2.ScrapeResponse:
        """Returns the content scraped from an HTML page"""

        # scrape the content from the data
        content = scrape(market=request.market, model=request.model, html=request.data)

        content_struct = Struct()
        content_struct.update(content)

        response = scraper_pb2.ScrapeResponse(content=content_struct)

        return response
