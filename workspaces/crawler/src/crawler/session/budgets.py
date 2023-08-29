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

import jsonlines
import os
import random

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from statistics import median_high
from typing import Callable, Protocol
from uuid import uuid4

@dataclass
class Record:
    crawler_id: str
    url: str
    code: int
    budget: str
    delay: float
    respond_time: float
    recommendation: uuid4
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Recommendation:
    """Simple class for budget recommendations"""

    id: uuid4 = field(default_factory=uuid4)
    delay: float = 1
    connections: int = 1
    records: list[Record] = field(default_factory=list)
    volume: str = "local"

    def success_rate(self) -> float:
        # Percentage of successful connections
        ret = len([con for con in self.recordds if con.code == 200]) / len(
            self.records
        )

        return ret

    def respond_time(self) -> float:
        # (High) Median respond time of the connections
        respond_times: list[float] = list(map(lambda con: con.respond_time, self.records))
        ret: float = median_high(respond_times)
        return ret

    def register(self, record: Record) -> None:
        """Include a new record and store it"""
        file_name: str = "records.jsonl"
        file_path: str = os.path.join(self.volume, file_name)
        data = record.__dict__
        
        with jsonlines.open(file_path, mode="a+", encoding="utf-8") as f:
            f.write(data)

        self.records.append(record)

    def record(
        self, response, name: str, url: str, response_code: int, elapsed, crawler_id: str
    ) -> None:
        if not response:
            return
        
        rec = Record(
            crawler_id=crawler_id,
            code=response_code,
            respond_time=elapsed,
            url=url,
            budget=name,
            delay=self.delay,
            recommendation=self.id,
        )

        self.register(rec)


@dataclass
class BudgetProtocol(Protocol):
    @abstractmethod
    def calculate(self) -> Recommendation:
        raise NotImplementedError

    @abstractmethod
    def consume(self) -> Recommendation:
        raise NotImplementedError


@dataclass
class Budget(BudgetProtocol):
    """Base for Budgets

    Attributes:
        recommendation (Recommendation): Current budget recommendation
        records (list[Record]): List of Records from previous requests.

        _recommendations (list[Recommendation]): List of previous recommendations
    """

    recommendation: Recommendation = field(default_factory=Recommendation)
    _recomendations: list[Recommendation] = field(default_factory=list)

    _MIN_DELAY: float = 1
    _MIN_CONNECTIONS: float = 1

    @property
    def connections(self) -> float:
        if self.recommendation.connections < self._MIN_CONNECTIONS:
            self.calculate()

        return self.recommendation.connections

    @property
    def delay(self) -> float:
        return random.uniform(self._MIN_DELAY, self.recommendation.delay)

    def consume(self) -> Recommendation:
        """Consume one connection from the current recommendation

        Returns:
            Recommendation: Current budget recommendation
        """
        # If there is no consummer yet, or connections left calculate a new budget
        if self.recommendation.connections < self._MIN_CONNECTIONS:
            self.calculate()

        # Consume one connection from the budget
        self.recommendation.connections -= 1

        return self.recommendation


@dataclass
class BudgetFactory:
    budgets = {}

    @classmethod
    def get_budget(cls, budget: str) -> Budget:
        if budget in cls.budgets:
            return cls.budgets[budget]

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls: Budget) -> Budget:
            cls.budgets[name] = decorator_cls

            return decorator_cls

        return decorator

@BudgetFactory.register("simple")
class SimpleBudget(Budget):
    name: str = "simple"

    _MAX_DELAY: float = 5
    _MAX_CONNECTIONS: float = 5

    def calculate(self) -> Recommendation:
        delay: float = random.uniform(self._MIN_DELAY, self._MAX_DELAY)
        ret: Recommendation = Recommendation(
            delay=delay, connections=self._MAX_CONNECTIONS
        )

        # Add the current budget to the recommendations and empty it
        self._recomendations.append(self.recommendation)
        self.recommendation = ret

        return ret
