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

# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ms_storage/protos/storage.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1fms_storage/protos/storage.proto\x12\x07storage\x1a\x1cgoogle/protobuf/struct.proto\"\xa2\x01\n\x0cStoreRequest\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12)\n\x05pages\x18\x03 \x03(\x0b\x32\x1a.storage.StoreRequest.Page\x1aH\n\x04Page\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x12%\n\x04meta\x18\x03 \x01(\x0b\x32\x17.google.protobuf.Struct\"P\n\rStoreResponse\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\x14\n\x07n_pages\x18\x03 \x01(\x05H\x00\x88\x01\x01\x42\n\n\x08_n_pages\"/\n\x0ePendingRequest\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\"?\n\x0fPendingResponse\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\r\n\x05pages\x18\x03 \x03(\t\"<\n\x0c\x43heckRequest\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\r\n\x05pages\x18\x03 \x03(\t\"=\n\rCheckResponse\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\r\n\x05pages\x18\x03 \x03(\t2\xbd\x01\n\x07Storage\x12\x38\n\x05Store\x12\x15.storage.StoreRequest\x1a\x16.storage.StoreResponse\"\x00\x12>\n\x07Pending\x12\x17.storage.PendingRequest\x1a\x18.storage.PendingResponse\"\x00\x12\x38\n\x05\x43heck\x12\x15.storage.CheckRequest\x1a\x16.storage.CheckResponse\"\x00\x62\x06proto3')



_STOREREQUEST = DESCRIPTOR.message_types_by_name['StoreRequest']
_STOREREQUEST_PAGE = _STOREREQUEST.nested_types_by_name['Page']
_STORERESPONSE = DESCRIPTOR.message_types_by_name['StoreResponse']
_PENDINGREQUEST = DESCRIPTOR.message_types_by_name['PendingRequest']
_PENDINGRESPONSE = DESCRIPTOR.message_types_by_name['PendingResponse']
_CHECKREQUEST = DESCRIPTOR.message_types_by_name['CheckRequest']
_CHECKRESPONSE = DESCRIPTOR.message_types_by_name['CheckResponse']
StoreRequest = _reflection.GeneratedProtocolMessageType('StoreRequest', (_message.Message,), {

  'Page' : _reflection.GeneratedProtocolMessageType('Page', (_message.Message,), {
    'DESCRIPTOR' : _STOREREQUEST_PAGE,
    '__module__' : 'ms_storage.protos.storage_pb2'
    # @@protoc_insertion_point(class_scope:storage.StoreRequest.Page)
    })
  ,
  'DESCRIPTOR' : _STOREREQUEST,
  '__module__' : 'ms_storage.protos.storage_pb2'
  # @@protoc_insertion_point(class_scope:storage.StoreRequest)
  })
_sym_db.RegisterMessage(StoreRequest)
_sym_db.RegisterMessage(StoreRequest.Page)

StoreResponse = _reflection.GeneratedProtocolMessageType('StoreResponse', (_message.Message,), {
  'DESCRIPTOR' : _STORERESPONSE,
  '__module__' : 'ms_storage.protos.storage_pb2'
  # @@protoc_insertion_point(class_scope:storage.StoreResponse)
  })
_sym_db.RegisterMessage(StoreResponse)

PendingRequest = _reflection.GeneratedProtocolMessageType('PendingRequest', (_message.Message,), {
  'DESCRIPTOR' : _PENDINGREQUEST,
  '__module__' : 'ms_storage.protos.storage_pb2'
  # @@protoc_insertion_point(class_scope:storage.PendingRequest)
  })
_sym_db.RegisterMessage(PendingRequest)

PendingResponse = _reflection.GeneratedProtocolMessageType('PendingResponse', (_message.Message,), {
  'DESCRIPTOR' : _PENDINGRESPONSE,
  '__module__' : 'ms_storage.protos.storage_pb2'
  # @@protoc_insertion_point(class_scope:storage.PendingResponse)
  })
_sym_db.RegisterMessage(PendingResponse)

CheckRequest = _reflection.GeneratedProtocolMessageType('CheckRequest', (_message.Message,), {
  'DESCRIPTOR' : _CHECKREQUEST,
  '__module__' : 'ms_storage.protos.storage_pb2'
  # @@protoc_insertion_point(class_scope:storage.CheckRequest)
  })
_sym_db.RegisterMessage(CheckRequest)

CheckResponse = _reflection.GeneratedProtocolMessageType('CheckResponse', (_message.Message,), {
  'DESCRIPTOR' : _CHECKRESPONSE,
  '__module__' : 'ms_storage.protos.storage_pb2'
  # @@protoc_insertion_point(class_scope:storage.CheckResponse)
  })
_sym_db.RegisterMessage(CheckResponse)

_STORAGE = DESCRIPTOR.services_by_name['Storage']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _STOREREQUEST._serialized_start=75
  _STOREREQUEST._serialized_end=237
  _STOREREQUEST_PAGE._serialized_start=165
  _STOREREQUEST_PAGE._serialized_end=237
  _STORERESPONSE._serialized_start=239
  _STORERESPONSE._serialized_end=319
  _PENDINGREQUEST._serialized_start=321
  _PENDINGREQUEST._serialized_end=368
  _PENDINGRESPONSE._serialized_start=370
  _PENDINGRESPONSE._serialized_end=433
  _CHECKREQUEST._serialized_start=435
  _CHECKREQUEST._serialized_end=495
  _CHECKRESPONSE._serialized_start=497
  _CHECKRESPONSE._serialized_end=558
  _STORAGE._serialized_start=561
  _STORAGE._serialized_end=750
# @@protoc_insertion_point(module_scope)
