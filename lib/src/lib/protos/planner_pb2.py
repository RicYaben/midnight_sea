# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: lib/src/lib/protos/planner.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n lib/src/lib/protos/planner.proto\x12\x07planner\x1a\x1cgoogle/protobuf/struct.proto\"\x1d\n\x0bPlanRequest\x12\x0e\n\x06market\x18\x01 \x01(\t\"5\n\x0cPlanResponse\x12%\n\x04plan\x18\x01 \x01(\x0b\x32\x17.google.protobuf.Struct2C\n\x07Planner\x12\x38\n\x07GetPlan\x12\x14.planner.PlanRequest\x1a\x15.planner.PlanResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'lib.src.lib.protos.planner_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_PLANREQUEST']._serialized_start=75
  _globals['_PLANREQUEST']._serialized_end=104
  _globals['_PLANRESPONSE']._serialized_start=106
  _globals['_PLANRESPONSE']._serialized_end=159
  _globals['_PLANNER']._serialized_start=161
  _globals['_PLANNER']._serialized_end=228
# @@protoc_insertion_point(module_scope)