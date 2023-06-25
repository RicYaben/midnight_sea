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
