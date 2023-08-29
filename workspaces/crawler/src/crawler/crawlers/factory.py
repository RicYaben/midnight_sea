from dataclasses import dataclass
from typing import Any, Callable
from crawler.crawlers.interfaces import Validator

@dataclass
class ValidatorFactory:
    validators = {}

    @classmethod
    def get_validator(cls, validator: str) -> Validator:
        return cls.validators.get(validator)

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls: Validator) -> Validator:
            cls.validators[name] = decorator_cls
            return decorator_cls

        return decorator
    
    @classmethod
    def create_validators(cls, sections: dict[str, dict[str, Any]]) -> dict[str, list[Validator]]:

        ret: dict = dict()
        for sec_name, section in sections.items():
            for name, conditions in section.items():
                validator = cls.validators.get(name)

                if not validator:
                    continue

                instance = validator(**conditions)

                if sec_name not in ret:
                    ret[sec_name] = []

                ret[sec_name].append(instance)

        return ret
