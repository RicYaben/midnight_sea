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

"""This Package contains a Crawler handler that will decide how to perform the crawling
"""
import os
import urllib.parse


from dataclasses import dataclass

from crawler.crawlers.interfaces import CrawlerProtocol
from crawler.session.session import SessionManager

@dataclass
class Crawler(CrawlerProtocol):
    volume: str = "local"

    def crawl(self, session: SessionManager, url: str, validate: bool = True):
        """Crawls the content of some page and returns the response"""
        # Clean the url
        clean = self.clean(url)

        # Request the page
        response = session.request(clean)

        # Validate the response if necessary
        if not validate:
            return

        # If there is a response continue, otherwise
        # try again without validation this time
        if not response:
            return self.crawl(session=session, url=url, validate=False)

        valid = self.validate(response)
        if valid:
            return response

        with open(os.path.join(self.volume, "response.html"), "wb") as f:
            f.write(response.content)
            
        # Re-authenticate if the response is not valid
        session.auth(self.market)
        return self.crawl(session=session, url=url, validate=False)

    def validate(self, response) -> bool:
        """Validates the response"""
        for section_validators in self.validators.values():
            for validator in section_validators:
                valid = validator.isValid(response)
                if not valid:
                    return False

        return True

    def clean(self, url: str) -> str:
        """Simple clean method to add the URL domain"""
        # Remove starting paths
        url = url[1:] if url.startswith("/") else url
        res = ""

        if self.path:
            url = url + self.path

        # Build the url
        for path in [self.domain, url]:
            res = urllib.parse.urljoin(res, path)

        return res


