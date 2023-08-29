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

"""
This package contains model classes to store records in the database
"""

import uuid

from sqlalchemy import (
    Column,
    TypeDecorator,
    UniqueConstraint,
    String,
    DateTime,
    Float,
    Integer,
)

from sqlalchemy import exc
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import CHAR
from sqlalchemy.sql.schema import ForeignKey, Table

from sqlalchemy_utils.types.choice import ChoiceType
from storage.database.database import get_database, Base

class CRUD:
    """Simple CRUD operations for the models. This can be used to update or delete instances on premise.
    Similarly to the use of `save` methods on Django
    """

    __session = None

    @property
    def _session(self):
        if not self.__session:
            self.__session = get_database().session

        return self.__session

    def save(self):
        ses = self._session
        ses.add(self)
        return self.commit()

    def delete(self):
        ses = self._session
        ses.delete(self)
        return self.commit()

    def commit(self):
        # Attempt to apply the changes
        ses = self._session
        try:
            return ses.commit()
        except exc.IntegrityError:
            ses.rollback()


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """

    impl = CHAR(36)

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Mixin(CRUD):
    """
    Mixin model that implements common fields to be used by most models

    Attributes:
        id: Primary key
        creation_date: when the item was recorded. Depends on the database timezone
        last_modified: when the item was last modified
    """

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, unique=True)

    creation_date = Column(DateTime(timezone=True), default=func.now())
    last_modified = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )


class Crawl(Mixin, Base):
    """This model sumarises the results of a crawl

    Args:
        banner: Information about the crawler used. It might contain a version, platform and others.
        pages: Pages crawled from some market
    """

    __tablename__ = "crawl"

    banner = Column(String)
    pages = relationship("Page", backref="crawl", lazy=True)


class Market(Mixin, Base):
    """
    Table for storing Market objects

    Attributes:
        name: Name of the Market
        reputation: system used by the market to track the vendors behaviour
    """

    __tablename__ = "market"

    name = Column(String(200))

    pages = relationship(
        "Page",
        backref="market",
        lazy=True,
    )
    reputation = relationship("Reputation", back_populates="market", uselist=False)


class Reputation(Mixin, Base):
    """Reputation system of a Market

    Attributes:
        max_val: integer representing the maximum value allowed
        min_val: integer representing the minimum value allowed

        market: Market in where this can be found
    """

    __tablename__ = "reputation"

    max_val = Column(Integer, default=0)
    min_val = Column(Integer, default=5)

    market_id = Column(GUID, ForeignKey("market.id"))
    market = relationship("Market", back_populates="reputation")


class Vendor(Mixin, Base):
    """Market Vendor

    Attributes:
        username: Username of the vendor
        pgp: PGP public key of the vendor
        reputation: Representation of the reputation value
        shipping_from: Location from where the vendor is shipping
        shipping_to: Location to where the vendor is able to ship
    """

    __tablename__ = "vendor"

    # fields
    username = Column(String)
    pgp = Column(String)
    path = Column(String)
    reputation = Column(Float)

    # Feedback
    positive_fb = Column(Float)
    negative_fb = Column(Float)
    disputes_fb = Column(Float)
    total_fb = Column(Float)

    shipping_from = Column(String)
    shipping_to = Column(String)

    # relationships
    page_id = Column(GUID, ForeignKey("page.id", ondelete="CASCADE"))

    page = relationship(
        "Page",
        backref=backref("vendor", uselist=False),
        passive_deletes=True,
        cascade="all, delete",
    )

    def save(self):
        """If the model does not contain a reputation metrics, assume this is given
        by the other parameters. Then attempt to calculate the reputation and save the model.
        """
        if not self.reputation:
            from storage.events import reputation_fn

            rep = reputation_fn(
                negative=self.negative_fb,
                total=self.total_fb,
                disputes=self.disputes_fb,
            )
            if rep:
                self.reputation = rep

        # Save the instance
        super().save()


class Crypto(Mixin, Base):
    """Crypto currencies. Although this table only contains one column, it is
    necessary for creating M2M relationships.

    Attributes:
        name: Name of the crypto-currency
    """

    __tablename__ = "crypto"

    # fields
    name = Column(String)


item_cryptos_table = Table(
    "item_cryptos",
    Base.metadata,
    Column("item_id", ForeignKey("item.id"), primary_key=True),
    Column("crypto_id", ForeignKey("crypto.id"), primary_key=True),
)

vendor_items_table = Table(
    "vendor_items",
    Base.metadata,
    Column("vendor_id", ForeignKey("vendor.id", ondelete="SET NULL"), primary_key=True),
    Column("item_id", ForeignKey("item.id", ondelete="SET NULL"), primary_key=True),
)


class Item(Mixin, Base):
    """Item listing of some market

    Attributes:
        title: Title of the item card
        description: long description of the item found on the page

        price: price of the item
        currency: divisa of the price
        category: category in which the item was found

        page: page url and file containing the raw data

        cryptos: accepted cryptos
        vendor: user listing the item
    """

    CURRENCIES = [("EUR", "EUR"), ("USD", "USD"), ("GBP", "GBP"), ("CAD", "CAD")]

    __tablename__ = "item"

    # fields
    title = Column(String)
    description = Column(String)
    price = Column(Float)
    currency = Column(ChoiceType(CURRENCIES))
    category = Column(String(50))

    sold = Column(Float)
    stock = Column(Integer)

    # relationships
    page_id = Column(GUID, ForeignKey("page.id", ondelete="CASCADE"))

    page = relationship(
        "Page",
        backref="item",
        uselist=False,
        passive_deletes=True,
        cascade="all, delete",
    )

    # M2M
    cryptos = relationship(Crypto, secondary=item_cryptos_table, backref="items")
    vendor = relationship(Vendor, secondary=vendor_items_table, backref="items")


class Page(Mixin, Base):
    """
    This model stores information about individual pages.
    The pages are stored in the file system and need to be processed.

    Attributes:
        file: name of the file stored.
        url: string representation of the page URL i.e., the path to the page
        parsed: whether or not the file has been parsed.
        page_type: Type of the page. Vendor, Listing or so.
        market: market rel. in where the page was found
    """

    PAGES = [("vendor", "Vendor"), ("item", "Item")]

    __tablename__ = "page"
    __table_args__ = (UniqueConstraint("url", "market_id"),)

    file = Column(String(200))
    url = Column(String(200), nullable=False)
    page_type = Column(ChoiceType(PAGES))

    # Relationships
    market_id = Column(GUID, ForeignKey("market.id"))
    crawl_id = Column(GUID, ForeignKey("crawl.id"))
