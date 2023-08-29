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
This package contains functions and methods for connecting
and performing operations on a given database.
"""
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy import orm, exc
from sqlalchemy.engine import Engine, URL
from sqlalchemy.ext.declarative import declarative_base

from lib.logger.logger import log
from storage.database import interfaces

_db = None

Base = declarative_base()


@dataclass
class Database:
    """This class keeps a record of the database session."""

    session: orm.Session = field(default_factory=orm.Session)
    engine: Engine = None

    def get_url(self, db: interfaces.Database) -> URL:
        drivername: str = f"{db.dialect}+{db.driver}"
        return URL.create(
            drivername=drivername,
            username=db.username,
            password=db.password,
            host=db.address,
            port=db.port,
            database=db.db,
        )


    def connect(
        self,
        db: interfaces.Database
    ) -> orm.Session:
        """Connect to a database

        This method stablish a connection channel between the
        host and an external database.
        The connection will be formed after creating a url that will be used
        to identify the database host.

        Args:
            db: DatabaseConfig

        Return:
            connection: A connection channel to the database
        """

        # To make it simpler, create a URL to connect
        url: URL = self.get_url(db)
        log.debug("Connecting to database...")

        # Create a database engine that we can connect to
        engine: Engine = create_engine(url, echo=False, echo_pool=False)
        engine.execution_options(stream_results=True)

        # Bind the engine to a session to ensure db consistency
        # We set the `future` attribute to True to utilise the `select`
        # function later on to filter statements rather than making raw queries
        session: orm.Session = orm.sessionmaker(bind=engine, future=True)

        self.session = session()
        self.engine = engine

        log.info("Connected to database")

        return session

    def load_models(self):
        if self.engine:
            log.debug("Loading models...")

            Base.metadata.create_all(
                self.engine, Base.metadata.tables.values(), checkfirst=True
            )

    def get_or_create(
        self, model, defaults: dict[Any, Any] = {}, **kwargs
    ) -> tuple[Any, bool]:
        """Return the instance of the object or create a new one if it did not exists

        Args:
            model ([type]): Model of the table in where the item should be found
            defaults (dict[Any, Any], optional): Default values for the model fields. Defaults to {}.

        Returns:
            Any: Instance of the (new) object
        """
        # Get the "only" instance of the object
        q = self.get(model, **kwargs)
        created = False

        if not q:
            # Create the item from the parameters given
            q, created = self.create(model, defaults, **kwargs)

        return q, created

    def get(self, model, **kwargs):
        try:
            # Check if there is an identity in the key arguments. This is sufficient
            if "id" in kwargs:
                return self.session.query(model).filter_by(id=kwargs["id"]).one()
            else:
                return self.session.query(model).filter_by(**kwargs).one()
        except orm.exc.NoResultFound as e:
            log.error(e)
            log.warning(f"Item not found: \nmodel: {model}\nArgs: {kwargs}")

    def create(
        self, model, defaults: dict[Any, Any] = {}, **kwargs
    ) -> tuple[Any, bool]:
        """Create a new instance in the database

        Args:
            model ([type]): Model of the table in where the item should be found
            defaults (dict[Any, Any], optional): Default values for the model fields. Defaults to {}.

        Raises:
            not_found: The item could not be created nor found in the db

        Returns:
            Any: Instance of the (new) object
        """

        # Make a dictionary with all the values
        params = defaults.copy()
        params.update(kwargs)

        try:
            # Create the instance and add it to the q on the session
            instance = model(**params)
            instance.save()
            return instance, True
        except exc.IntegrityError:

            # Remove the intance added
            self.session.rollback()

            # Query to get the item, apparently there is one in the db
            query = self.session.query(model).filter_by(**kwargs)
            try:
                instance = query.one()
                return instance, False
            except orm.exc.NoResultFound as not_found:
                raise not_found

    def save(self, *instances):
        """This method can be used to save multiple instances simultaneously.
        It should not be used for single instances though. Every model includes a `save` method
        that should be called instead.
        """
        if instances:
            # Add each instance to the commit q
            self.session.add_all(instances)

            # Attempt to apply the changes
            try:
                self.session.commit()
                return instances
            except exc.IntegrityError:
                self.session.rollback()

    def delete(self, instance):
        if instance:
            self.session.delete(instance)


def create_database(conf: interfaces.Database) -> Database:
    global _db

    log.info("Loading database connection...")

    db = Database()
    db.connect(conf)
    db.load_models()

    _db = db
    return db

def get_database() -> Database | None: 
    global _db
    return _db