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

import csv
import math
import os
import random
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from statistics import median_high, median_low, stdev
from typing import Any, Callable, Dict, Protocol, Sequence
from uuid import uuid4

from ms_crawler.globals import MAX_CONNECTIONS, MAX_DELAY, VOLUME, SERVICE_ID


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
    records: Sequence[Record] = field(default_factory=list)

    def success_rate(self) -> float:
        # Percentage of successful connections
        ret = len(list(filter(lambda con: con.code == 200, self.records))) / len(
            self.records
        )

        return ret

    def respond_time(self) -> float:
        # (High) Median respond time of the connections
        respond_times: Sequence[float] = list(map(lambda con: con.respond_time, self.records))
        ret: float = median_high(respond_times)
        return ret

    def register(self, record: Record) -> None:
        """Include a new record and store it"""
        filepath: str = f"{VOLUME}/records.csv"
        data = record.__dict__
        
        # Create the file and write the header to the file
        if not os.path.exists(filepath):
            with open(filepath, "w", newline="") as outcsv:
                writer = csv.DictWriter(outcsv, fieldnames=data.keys())
                writer.writeheader()
            
        # Append a new row
        with open(filepath, "a+") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writerow(data)

        self.records.append(record)

    def record(
        self, response, name: str, url: str, response_code: int, elapsed
    ) -> None:
        if not response:
            return
        
        rec = Record(
            crawler_id=SERVICE_ID,
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
        records (Sequence[Record]): List of Records from previous requests.

        _recommendations (Sequence[Recommendation]): List of previous recommendations
    """

    recommendation: Recommendation = field(default_factory=Recommendation)
    _recomendations: Sequence[Recommendation] = field(default_factory=list)

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


@BudgetFactory.register("logarithmic")
@dataclass
class LogarithmicBudget(Budget):
    name: str = "logarithmic"

    _MAX_DELAY: float = MAX_DELAY
    _MAX_CONNECTIONS: float = MAX_CONNECTIONS

    def calculate(self) -> Recommendation:
        # Get the medians of the previous records
        medians: Dict[Any, Any] = self._record_medians()

        # Connections
        sc: float = medians.get("success_rate")
        conn_deviation: float = self._deviation(
            median=sc, val=float(self.recommendation.connections)
        )
        conn_smooth: float = self._smooth_fn(
            max=self._MAX_CONNECTIONS,
            min=self._MIN_CONNECTIONS,
            deviation=conn_deviation,
        )
        conns = int(conn_smooth)

        # Delay
        rs: float = medians.get("respond_time")
        delay_deviation: float = self._deviation(
            median=rs, val=self.recommendation.delay
        )
        delay: float = self._smooth_fn(
            max=self._MAX_DELAY, min=self._MIN_DELAY, deviation=delay_deviation
        )

        # Recommendation
        recommendation: Recommendation = Recommendation(delay=delay, connections=conns)

        # Add the current budget to the recommendations and empty it
        self._recomendations.append(self.recommendation)
        self.recommendation = recommendation

        return recommendation

    def _deviation(self, median: float, val: float) -> float:
        deviation = stdev([median, val])

        # Convert the deviation sign to indicate the growth direction
        if (val - median) < 0:
            deviation *= -1

        return deviation

    def _record_medians(self) -> Dict[Any, Any]:

        connections = [
            recomendation.success_rate() for recomendation in self._recomendations
        ]
        respond_times = [
            recomendation.respond_time() for recomendation in self._recomendations
        ]

        if not connections:
            connections = [1]

        if not respond_times:
            respond_times = [1]

        respond_time = median_high(respond_times)  # (low) Median of the success rate
        success_rate = median_low(connections)  # (high) Median of the respond time

        ret: dict = dict(success_rate=success_rate, respond_time=respond_time)
        return ret

    def _smooth_fn(self, min: float, max: float, deviation: float) -> float:
        """Smoothes some value using a sigmoid function

            |        +++++
            |     +++
            |   +y....*
            | ++      .
            |++       .
            |+        .
            |_________x___

        Args:
            min (float): _description_
            max (float): _description_
            boundary (float): _description_

        Returns:
            float: _description_
        """
        # [2/28/2022] TODO: Find a good growth algorithm
        sigmoid = lambda x: 1 / (1 + math.exp(-x))  # Basic sigmoid activation function
        pos = lambda x: 1 / (1 + math.exp(abs(x)))  # Some correction function
        correction = lambda x: pos(x) or 0.1

        # Calculate the corrected value
        t = deviation * -1  # growth rate
        corr = correction(deviation)
        value = sigmoid(t)

        # Calculate the corrected value.
        # This is given by the original sigmoid value, a range between [-1,1]
        # minus the corrected value, which is basically the absolute of the deviation from the median
        # Then it is divided by the difference of the corrected value. E.g:
        #   value = .2 <- growth rate
        #   corr = .2 <- corrected value
        #   div = .8 <- division
        # TODO: this is wrong!
        corrected_value = (value - corr) / ((1 - 2 * corr) or 0.1)

        # Calculate a prediction, which will be the corrected value times the difference
        # between the maximum and the minimum. E.g.:
        #   corrected_value = 0.5 |-> prediction = 10 - 4.5 = 5.5
        #   diff = 9              |
        prediction = max - (corrected_value * (max - min))

        print("Recomendation: ")
        print(value, corr, corrected_value, prediction)

        return prediction


@BudgetFactory.register("simple")
class SimpleBudget(Budget):
    name: str = "simple"

    _MAX_DELAY: float = MAX_DELAY
    _MAX_CONNECTIONS: float = MAX_CONNECTIONS

    def calculate(self) -> Recommendation:
        delay: float = random.uniform(self._MIN_DELAY, self._MAX_DELAY)
        ret: Recommendation = Recommendation(
            delay=delay, connections=self._MAX_CONNECTIONS
        )

        # Add the current budget to the recommendations and empty it
        self._recomendations.append(self.recommendation)
        self.recommendation = ret

        return ret
