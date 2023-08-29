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

from dataclasses import dataclass
import os
import pathlib
from lib.stubs.interfaces import LocalStubCls
import yaml

from lib.logger.logger import log
from lib.stubs.factory import StubFactory

from crawler.stubs.interfaces import Planner
from lib.protos.planner_pb2_grpc import PlannerStub
from crawler.strategies.plan import Plan

import crawler


@StubFactory.register("planner")
@dataclass
class PlannerService(Planner):
    _stub_cls = PlannerStub

    def get_plan(self, market: str) -> Plan:
        response = self.stub.GetPlan(market)
        plan: Plan = Plan(data=response.message.plan)

        return plan


@StubFactory.register("planner", True)
@dataclass
class LocalPlannerService(Planner):
    _stub_cls = LocalStubCls
    _plan_path: pathlib.Path = os.path.join(os.path.dirname(crawler.__file__), "../../dist", "plans")

    def get_plan(self, market: str) -> Plan | None:
        plan_filepath: str = "%s.yaml" % market

        p = os.path.join(self._plan_path, plan_filepath)
        if not os.path.exists(p):
            log.error("Plan for %s not found" % market)
            return

        with open(p, "r") as f:
            content = yaml.load(f, yaml.loader.SafeLoader)
            plan: Plan = Plan(data=content)
            return plan

        
