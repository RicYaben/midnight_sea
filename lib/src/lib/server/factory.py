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

"""This package contains the classes to stablish connections with the
rest of the services.

The package includes methods to start a server and communicate with
the other services, including challenges, elastic updates and more.
"""
import os
from concurrent import futures
from typing import Tuple

import grpc
from lib.conf.config import Host
from lib.logger import logger

class ServerFactory:

    @classmethod
    def _read_cert(cls) -> Tuple[bytes, bytes]:
        """Function to read the credentials from some files

        Args:
            key (str): Key path
            chain (str): Chain Path
            volume (str): Where the files are stored.
        Raises:
            FileNotFoundError: Error when the files can't be found
        Returns:
            Tuple: private key and chain
        """
        # Create common paths
        key_p, chain_p = [
            os.path.join("dist", "server", "server.%s" % p) for p in ["key", "crt"]
        ]

        # Validate the paths
        if not (os.path.isfile(key_p) and os.path.isfile(chain_p)):
            logger.warning(FileNotFoundError("Chain or Key not found"))
            return None, None

        # Read the private key
        with open(key_p, "rb") as f:
            private_key = f.read()

        # Read the chain
        with open(chain_p, "rb") as f:
            certificate_chain = f.read()

        return private_key, certificate_chain

    @classmethod
    def create_server(cls, host: Host, workers: int=10) -> grpc.Server:
        key, chain = cls._read_cert()

        # Create a server that can be used asynchronously
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=workers))

        # If there is a private key and certificate, build a secure port,
        # Otherwise it creates an insecure port.
        if key and chain:
            # Get the credentials to create a secure server
            creds = grpc.ssl_server_credentials(
                (
                    (
                        private_key,
                        cert_chain,
                    ),
                )
            )

            # Delete the sensitive data to stop leaks
            del private_key
            del cert_chain

            # Pass down the credentials
            server_port = server.add_secure_port(f"{host.address}:{host.port}", creds)

        else:
            server_port = server.add_insecure_port(f"{host.address}:{host.port}")
            logger.warning("Loaded insecure port")

        logger.debug(f"Server built to listen for connections on {host.address} {server_port}")

        return server


def start_server(server: grpc.Server):
    """Starts the server built

    Returns:
        server:    The server passed to the function
    """
    server.start()
    logger.info("Server started")
    server.wait_for_termination()

    return server
