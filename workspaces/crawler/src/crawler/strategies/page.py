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

import re
import tempfile

from typing import Any
from dataclasses import dataclass, field

import requests

from lib.logger.logger import log


@dataclass(order=True, unsafe_hash=True)
class Page:
    """Wrapper to store information about the page content

    Attributes:
        url (str): Relative Url to the page
        _file (TemporaryFile): Where the content is written
    """

    url: str
    meta: dict[Any, Any] = field(default_factory=dict)
    status_code: int = 0

    _file: tempfile.TemporaryFile = None
    _pk: str = ""

    @property
    def crawled(self) -> bool:
        # Return True if there is a file
        return self._file is not None

    @property
    def data(self) -> bytes:
        """Read the content of the file in bytes"""

        if self._file:
            self._file.seek(0)
            data = self._file.read()

            if data:
                return bytes(data)

        log.warning("Attempted to read from an empty Page file")

    @property
    def pk(self) -> str:
        # Slugify the url
        if not self._pk:
            self._pk = re.sub("[^a-zA-Z0-9 \n\.]", "_", self.url)
        return self._pk

    def store(self, response: requests.Response) -> tempfile.TemporaryFile:
        # Get the response and store the content on a temporary file
        if hasattr(response, "content"):
            self._file = tempfile.TemporaryFile()
            self._file.write(response.content)

        # Store the status code
        if hasattr(response, "status_code"):
            self.status_code = response.status_code

        log.debug("Content written in Temporary file")

        return self._file

    def close(self) -> None:
        if self._file:
            self._file.close()
            self._file = None

    def serialize(self) -> dict[Any, Any]:
        ret: dict = dict(
            url=self.url,
            data=self.data,
            meta=self.meta,
        )
        return ret



@dataclass
class PageParser:
    rex = re.compile(r"\$\{(?P<var>.*?)\}")

    def parse_to_pages(self, page: dict) -> list[Page]:
        path: str = page.get("path")
        ret = []

        if "vars" in page:
            v: dict = page.get("vars")

            for key, val in v.items():
                fn = getattr(self, f"replace_{key}")
                res = fn(path, val)
                ret += res
        else:
            ret = [path]

        name = page.get("name")
        pages = [Page(url=page, meta=dict(category=name)) for page in ret]

        return pages

    def replace_list(self, path, ls) -> list:
        ret = []
        for i in ls:
            sub = re.sub(self.rex, str(i), path)
            ret.append(sub)
        return ret

    def replace_range(self, path, ran) -> list:
        start, stop = ran
        ret = []
        for i in range(start, stop + 1):
            sub = re.sub(self.rex, str(i), path)
            ret.append(sub)
        return ret


def make_pages(sects) -> list[Page]:
    # Load the pages
    ret = []
    parser = PageParser()

    for sections in sects.values():
        for page in sections:
            res: list = parser.parse_to_pages(page)
            ret += res

    return ret
