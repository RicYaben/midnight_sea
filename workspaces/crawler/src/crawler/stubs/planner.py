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

import os
import pathlib
import yaml

from lib.logger import logger
from lib.stubs.factory import StubFactory

from crawler.stubs.interfaces import Planner
from lib.protos.planner_pb2_grpc import PlannerStub
from crawler.strategies.plan import Plan


@StubFactory.register("planner")
class PlannerService(Planner):

    _stub_cls = PlannerStub

    def plan(self, market: str) -> Plan:
        response = self.stub.GetPlan(market)
        plan: Plan = Plan(data=response.message.plan)

        return plan


@StubFactory.register("planner", True)
class LocalPlannerService(Planner):
    _plan_path: pathlib.Path = os.path.join("dist", "plans")

    def plan(self, market: str) -> Plan:
        plan_filepath: str = "%s.yaml" % market

        p = os.path.join(self._plan_path, plan_filepath)
        if os.path.exists(p):
            with open(p, "r") as f:
                content = yaml.load(f, yaml.loader.SafeLoader)
                plan: Plan = Plan(data=content)
                return plan
        else:
            logger.error("Plan for %s not found" % market)
