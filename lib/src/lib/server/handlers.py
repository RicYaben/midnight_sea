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
Creates an Api Endpoint that allows communication with the Storage service.
"""
from typing import Any
import grpc
from lib import protos
import sys

def lazy_get_handler(name: str):
    """Returns the handler of the service, generated by the .proto file"""
    service_fmt = f"{name.lower()}_pb2_grpc"
    ret = getattr(sys.modules[protos.__name__], service_fmt)

    return ret


def _add_service_endpoints_to_server(
    servicer, name: str, server: grpc.Server
) -> None:
    """Retrieves the API endpoint for some class and adds it to the server"""

    # Get the grpc module
    handler = lazy_get_handler(name)

    # Capitalise the name of the service to match the name of the class
    add_handler = getattr(handler, f"add_{name.capitalize()}Servicer_to_server")

    # Add the handler to the server
    add_handler(servicer(), server)


def add_handlers(server: grpc.Server, servicer: Any, name: str) -> grpc.Server:
    """Add the service handlers to a server"""

    _add_service_endpoints_to_server(name=name, servicer=servicer, server=server)

    return server