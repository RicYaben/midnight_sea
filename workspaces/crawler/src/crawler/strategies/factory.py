from dataclasses import dataclass
from typing import Callable
from crawler.strategies.interfaces import Strategy


@dataclass
class StrategyFactory:
    strategies = {}

    @classmethod
    def get_strategy(cls, strategy: str) -> Strategy:
        return cls.strategies.get(strategy, Strategy)

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls: Strategy) -> Strategy:
            cls.strategies[name] = decorator_cls

            return decorator_cls

        return decorator
