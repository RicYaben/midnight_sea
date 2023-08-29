from abc import abstractmethod
from typing import Protocol
from sqlalchemy import inspect
from sqlalchemy.types import Float, Integer
from dataclasses import dataclass, field

from storage.database.database import Database, get_database
from sqlalchemy_utils.types.choice import ChoiceType


@dataclass
class ApiEndpointProtocol(Protocol):
    """API abstraction base

    Args:
        db: Database connection.
        model: Database model
    """

    db: Database
    _db: Database = field(init=False, repr=False, default=get_database)

    model = None

    @property
    def db(self) -> Database:
        return self._db

    @db.setter
    def db(self, v: Database = None) -> None:
        if type(v) is property:
            v = ApiEndpointProtocol._db()
        self._db = v

    @abstractmethod
    def store(self, force: bool = True, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, instance, **kwargs):
        raise NotImplementedError


@dataclass
class ApiEndpoint(ApiEndpointProtocol):
    """A mixin to be used by various models without changing anything else than the model"""

    def delete(self, instance):
        self.db.delete(instance)

    def update(self, instance, **kwargs):
        related_fields: dict = self._get_related_columns()

        # Remove the related fields from the kwargs
        params: dict = {
            key: val for key, val in kwargs.items() if key not in related_fields
        }

        # Set the values
        for field_name, val in params.items():
            setattr(instance, field_name, val)

        # Update the instance with the values of the related fields using their
        # primary key to find the other instances
        for name, rel in related_fields.items():
            rel_params = kwargs.pop(name, None)
            if rel_params:
                self._set_related_field(instance, name, rel, rel_params)

        instance.save()

    def store(self, force: bool = True, **kwargs):
        related_fields: dict = self._get_related_columns()

        # Remove the related fields from the kwargs
        params: dict = {
            key: val
            for key, val in kwargs.items()
            if key not in related_fields  # and key not in weird_fields
        }

        # Create an instance of the model
        if force:
            instance = self.model(**params)
        else:
            instance, _ = self.db.get_or_create(self.model, **params)

        # Update the instance with the values of the related fields using their
        # primary key to find the other instances
        for name, rel in related_fields.items():
            rel_params = kwargs.pop(name, None)
            if rel_params:
                self._set_related_field(instance, name, rel, rel_params)

        instance.save()
        return instance

    def _format_field(self, value: any, field_name: str):
        columns = inspect(self.model).c

        fields = {
            Float: float,
            Integer: int,
        }

        if not value:
            return

        for c in columns:
            if c.name == field_name:
                col_type = type(c.type)
                if col_type not in fields:
                    return value

                t = fields[col_type]
                formatted = t(value)
                return formatted

        raise Exception(f"Field {field_name} not found")

    def _get_related_columns(self):
        """Returns a list of related columns"""
        return inspect(self.model).relationships

    def _get_weird_columns(self):
        weird = [ChoiceType]
        columns = inspect(self.model).c

        return [col.name for col in columns if col.type in weird]

    def _set_related_field(self, instance, name: str, relationship, params):
        """Sets the value of a Related Field using the parameters to get or
        create a new instance of the related model.
        The related model is captured from the field.

        Args:
            instance: Instance of a model
            name (str): Name of the field
            relationship: Relationship object
        """

        # Get an instance of the related model
        rel_model = relationship.mapper.class_
        rel_instance, _ = self.db.get_or_create(rel_model, **params)

        # Add the instance to the field or set it
        if relationship.uselist:
            # Get the field to update
            field = getattr(instance, name)
            field.append(rel_instance)
        else:
            setattr(instance, name, rel_instance)