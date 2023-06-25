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

"""
Main entrypoint for the application
"""
from ms_crawler.client.stubs import Stubs, build_stubs
from ms_crawler.globals import ALLOWED
from ms_crawler.strategies.strategy import strat


def main():
    # Build the stubs
    stubs: Stubs = build_stubs()

    stubs: dict = {stub: stubs.get_stub(stub) for stub in ALLOWED}

    # Start the crawler
    strat(**stubs)


if __name__ == "__main__":
    main()
