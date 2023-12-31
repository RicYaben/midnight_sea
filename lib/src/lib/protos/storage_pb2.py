# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: lib/src/lib/protos/storage.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n lib/src/lib/protos/storage.proto\x12\x07storage\x1a\x1cgoogle/protobuf/struct.proto\"\xa2\x01\n\x0cStoreRequest\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12)\n\x05pages\x18\x03 \x03(\x0b\x32\x1a.storage.StoreRequest.Page\x1aH\n\x04Page\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\x12%\n\x04meta\x18\x03 \x01(\x0b\x32\x17.google.protobuf.Struct\"P\n\rStoreResponse\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\x14\n\x07n_pages\x18\x03 \x01(\x05H\x00\x88\x01\x01\x42\n\n\x08_n_pages\"/\n\x0ePendingRequest\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\"?\n\x0fPendingResponse\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\r\n\x05pages\x18\x03 \x03(\t\"<\n\x0c\x43heckRequest\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\r\n\x05pages\x18\x03 \x03(\t\"=\n\rCheckResponse\x12\x0e\n\x06market\x18\x01 \x01(\t\x12\r\n\x05model\x18\x02 \x01(\t\x12\r\n\x05pages\x18\x03 \x03(\t2\xbd\x01\n\x07Storage\x12\x38\n\x05Store\x12\x15.storage.StoreRequest\x1a\x16.storage.StoreResponse\"\x00\x12>\n\x07Pending\x12\x17.storage.PendingRequest\x1a\x18.storage.PendingResponse\"\x00\x12\x38\n\x05\x43heck\x12\x15.storage.CheckRequest\x1a\x16.storage.CheckResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'lib.src.lib.protos.storage_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_STOREREQUEST']._serialized_start=76
  _globals['_STOREREQUEST']._serialized_end=238
  _globals['_STOREREQUEST_PAGE']._serialized_start=166
  _globals['_STOREREQUEST_PAGE']._serialized_end=238
  _globals['_STORERESPONSE']._serialized_start=240
  _globals['_STORERESPONSE']._serialized_end=320
  _globals['_PENDINGREQUEST']._serialized_start=322
  _globals['_PENDINGREQUEST']._serialized_end=369
  _globals['_PENDINGRESPONSE']._serialized_start=371
  _globals['_PENDINGRESPONSE']._serialized_end=434
  _globals['_CHECKREQUEST']._serialized_start=436
  _globals['_CHECKREQUEST']._serialized_end=496
  _globals['_CHECKRESPONSE']._serialized_start=498
  _globals['_CHECKRESPONSE']._serialized_end=559
  _globals['_STORAGE']._serialized_start=562
  _globals['_STORAGE']._serialized_end=751
# @@protoc_insertion_point(module_scope)
