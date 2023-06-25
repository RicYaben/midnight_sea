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

from abc import abstractmethod
from typing import Callable, Protocol
from sqlalchemy import Sequence, inspect
from sqlalchemy.types import Float, Integer
from dataclasses import dataclass, field

from ms_storage.globals import logger
from ms_storage.database.models import Item, Page, Vendor
from ms_storage.database.database import Database, get_database
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
            # val = self._format_field(value=val, field_name=field_name)
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
                if not col_type in fields:
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


@dataclass
class ApiFactory:
    """Factory for the API endpoints"""

    endpoints = {}

    @classmethod
    def get_endpoint(cls, endpoint: str) -> ApiEndpoint:
        if endpoint in cls.endpoints:
            return cls.endpoints[endpoint]()

    @classmethod
    def register(cls, name: str) -> Callable:
        def decorator(decorator_cls: ApiEndpoint) -> ApiEndpoint:
            cls.endpoints[name] = decorator_cls

            return decorator_cls

        return decorator


@ApiFactory.register("page")
class PageEndpoint(ApiEndpoint):
    model = Page

    def find(self, url, market):
        try:
            instance = (
                self.db.session.query(self.model)
                .filter(self.model.market.has(name=market), self.model.url == url)
                .one_or_none()
            )

            return instance
        except:
            pass

    def placeholders(self, urls: Sequence[str], market: str, page_type: str):
        for url in urls:
            page = {"market": {"name": market}, "page_type": page_type, "url": url}
            self.store(force=False, **page)

    def exists(
        self,
        market: str,
        pages: Sequence[str],
        page_type: str,
        placeholders: bool = True,
    ):
        """Check the database for some pages.

        We do not need to know the type of the page, only the url and the market. It might
        be that two markets follow identical structure, perhaps in the future as more markets
        flower in the Dark Net, and the owners reuse their assets.

        Args:
            market (str): The market in where the pages should be found.
            pages (Sequence[str]): List of page urls
            model (str): Name of the type of the page i.e. vendor, item, etc.
            placeholders (bool): Wether or not to store the values not found as placeholders

        Returns:
            q: A query list object
        """
        logger.debug("Checking pages...")
        # Filter the database to get the pages found from the list for the market
        q = (
            self.db.session.query(self.model)
            .filter(self.model.url.in_(pages), self.model.market.has(name=market))
            .all()
        )

        # Create the page placeholders for those pages that were not found
        if placeholders:
            logger.debug("Creating placeholders...")

            found = [page.url for page in q]
            not_found = [url for url in pages if url not in found]
            self.placeholders(urls=not_found, market=market, page_type=page_type)

        return q

    def pending(self, market: str = None, page_type: str = None) -> Sequence:
        """Return the list of pending pages to be crawl"""
        logger.debug("Checking pending...")

        # Get the pages with no file in it
        q = self.db.session.query(self.model).filter(self.model.file == None)

        if market:
            q = q.filter(self.model.market.has(name=market))

        if page_type:
            q = q.filter(self.model.page_type == page_type)

        # q = q.filter(self.model.status_code <= 300)

        # Limit the query to 50 items, to make it manageable
        q = q.limit(50).all()
        return q


@ApiFactory.register("item")
class ItemEndpoint(ApiEndpoint):
    model = Item


@ApiFactory.register("vendor")
class VendorEndpoint(ApiEndpoint):
    model = Vendor
