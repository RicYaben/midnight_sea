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

# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from ms_crawler.protos import scraper_pb2 as ms__crawler_dot_protos_dot_scraper__pb2


class ScraperStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Scrape = channel.unary_unary(
                '/scraper.Scraper/Scrape',
                request_serializer=ms__crawler_dot_protos_dot_scraper__pb2.ScrapeRequest.SerializeToString,
                response_deserializer=ms__crawler_dot_protos_dot_scraper__pb2.ScrapeResponse.FromString,
                )


class ScraperServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Scrape(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ScraperServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Scrape': grpc.unary_unary_rpc_method_handler(
                    servicer.Scrape,
                    request_deserializer=ms__crawler_dot_protos_dot_scraper__pb2.ScrapeRequest.FromString,
                    response_serializer=ms__crawler_dot_protos_dot_scraper__pb2.ScrapeResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'scraper.Scraper', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Scraper(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Scrape(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/scraper.Scraper/Scrape',
            ms__crawler_dot_protos_dot_scraper__pb2.ScrapeRequest.SerializeToString,
            ms__crawler_dot_protos_dot_scraper__pb2.ScrapeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
