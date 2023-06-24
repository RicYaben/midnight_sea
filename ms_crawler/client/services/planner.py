import os
import pathlib
import yaml

from ms_crawler.globals import VOLUME, logger
from ms_crawler.client.interfaces import (
    ExService,
    Planner,
    Service,
    ServiceFactory,
)
from ms_crawler.protos.planner_pb2_grpc import PlannerStub
from ms_crawler.strategies.plan import Plan


@ServiceFactory.register("planner")
class PlannerService(ExService, Planner):

    _stub_class = PlannerStub

    def plan(self, market: str) -> Plan:
        response = self.stub.GetPlan(market)
        plan: Plan = Plan(data=response.message.plan)

        return plan


@ServiceFactory.register("local_planner")
class LocalPlannerService(Service, Planner):

    _plan_path: pathlib.Path = os.path.join(VOLUME, "plans")

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
