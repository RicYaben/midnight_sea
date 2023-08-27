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

from ms_storage.protos import crawler_pb2 as ms__storage_dot_protos_dot_crawler__pb2


class CrawlerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetCookies = channel.unary_unary(
                '/crawler.Crawler/GetCookies',
                request_serializer=ms__storage_dot_protos_dot_crawler__pb2.CookiesRequest.SerializeToString,
                response_deserializer=ms__storage_dot_protos_dot_crawler__pb2.CookiesResponse.FromString,
                )
        self.WaitForMarket = channel.unary_unary(
                '/crawler.Crawler/WaitForMarket',
                request_serializer=ms__storage_dot_protos_dot_crawler__pb2.MarketRequest.SerializeToString,
                response_deserializer=ms__storage_dot_protos_dot_crawler__pb2.MarketResponse.FromString,
                )


class CrawlerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetCookies(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def WaitForMarket(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CrawlerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetCookies': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCookies,
                    request_deserializer=ms__storage_dot_protos_dot_crawler__pb2.CookiesRequest.FromString,
                    response_serializer=ms__storage_dot_protos_dot_crawler__pb2.CookiesResponse.SerializeToString,
            ),
            'WaitForMarket': grpc.unary_unary_rpc_method_handler(
                    servicer.WaitForMarket,
                    request_deserializer=ms__storage_dot_protos_dot_crawler__pb2.MarketRequest.FromString,
                    response_serializer=ms__storage_dot_protos_dot_crawler__pb2.MarketResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'crawler.Crawler', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Crawler(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetCookies(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/crawler.Crawler/GetCookies',
            ms__storage_dot_protos_dot_crawler__pb2.CookiesRequest.SerializeToString,
            ms__storage_dot_protos_dot_crawler__pb2.CookiesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def WaitForMarket(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/crawler.Crawler/WaitForMarket',
            ms__storage_dot_protos_dot_crawler__pb2.MarketRequest.SerializeToString,
            ms__storage_dot_protos_dot_crawler__pb2.MarketResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)