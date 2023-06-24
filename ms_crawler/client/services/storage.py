import os
import json

from typing import Any, Dict, Sequence
from google.protobuf.struct_pb2 import Struct

from ms_crawler.globals import VOLUME, logger
from ms_crawler.client.interfaces import (
    ExService,
    Service,
    ServiceFactory,
    Storage,
)
from ms_crawler.strategies.content import Page

from ms_crawler.protos.storage_pb2 import (
    PendingRequest,
    StoreRequest,
    CheckRequest,
)
from ms_crawler.protos.storage_pb2_grpc import StorageStub


@ServiceFactory.register("storage")
class StorageService(ExService, Storage):
    _stub_class = StorageStub

    def store(self, pages: Sequence[Page], market: str, model: str) -> bool:
        """Send the content of the pages to the storage service

        Args:
            pages (Sequence[Page]): Page objects
            market (str): Name of the market
            model (str): Name of the model in where the pages must be stored
        Returns:
            bool: Whether the pages were stored successfully
        """
        # Serialise all the pages
        serialised = [page.serialize() for page in pages]
        serialised = [page for page in serialised if page["data"]]

        # Convert the meta into a struct object
        for page in serialised:
            s = Struct()
            s.update(page["meta"])
            page["meta"] = s

        request = StoreRequest(market=market, pages=serialised, model=model)
        response = self.stub.Store(request)

        return response

    def pending(self, market: str, model: str) -> Sequence[Dict[Any, Any]]:
        """Returns the list of pending pages to be crawled

        Args:
            market (str): Name of the market

        Returns:
            dict: List of Pages
        """
        logger.info(f"Requesting pending {model}(s)...")
        request = PendingRequest(market=market, model=model)
        response = self.stub.Pending(request)

        pages: Sequence[Page] = [Page(url=page) for page in response.pages]

        return pages

    def check(self, market: str, model: str, pages: Sequence[str]) -> Sequence[str]:
        """Return the list of pages that are found in the database with these attributes

        Args:
            market (str): Name of the market
            model (str): Name of the model as is in the database
            pages (Sequence[str]): List of pages to check

        Returns:
            Sequence[Page]: List of pages found in the database
        """
        request = CheckRequest(market=market, model=model, pages=pages)
        response = self.stub.Check(request)

        return response.pages


@ServiceFactory.register("local_storage")
class LocalStorageService(Service, Storage):
    _pending: Sequence[Page] = []

    def store(self, pages: Sequence[Page], market: str, model: str) -> bool:
        """Method to store locally the content of the pages

        Args:
            pages (Sequence[Page]): List of pages to store
            market (str): Name of the market to where they belong

        Returns:
            bool: Whether everything went alright
        """
        for page in pages:
            category = page.meta["category"] if "category" in page.meta else None

            fpath = [
                p for p in [category] if p
            ]  # NOTE: The page already contains a "model" field!
            local = os.path.join(VOLUME, "markets", market, model, *fpath)

            logger.debug("Storing item %s in %s" % (page.pk, local))

            # Create the folder if it does not exits
            if not os.path.exists(local):
                os.makedirs(local)

            data = page.data
            if data:
                with open(os.path.join(local, page.pk), "wb") as f:
                    f.write(data)

                # Close the temporary file
                page.close()

            else:
                logger.debug(f"Page {page.id} was empty!")

            # Remove the page from the pending
            self._remove_pending(page.pk)

        return True

    def pending(self, market: str, model: str) -> Sequence[Page]:
        """This function returns the list of pending pages to crawl

        Args:
            market (str): Name of the market being crawled
            model (str): Name of the table/folder in where the data is stored

        Returns:
            Sequence[Page]: A list of pending pages
        """

        # If there are pending files, returm them
        if not self._pending:
            # Check if the folder exists
            local = os.path.join(VOLUME, "markets", market, model)

            if not os.path.exists(local):
                os.makedirs(local)

            filepath = os.path.join(local, "pending.json")

            # Create the file if it does not exists or if we don't have access to it
            if not (os.path.isfile(filepath) and os.access(filepath, os.R_OK)):
                with open(filepath, "w") as wf:
                    json.dump({"pending": []}, wf)

            with open(filepath, "r") as f:
                data = json.load(f)

                # Set the pending pages to a list that we can retrieve
                self._pending = [Page(url=page) for page in data.get("pending")]

        return self._pending

    def _remove_pending(self, identifier: str) -> None:
        """Remove some pages from the pending list

        Args:
            identifier (str): String ID of the page
        """

        if self._pending:
            filtered_pages: Sequence = list(
                filter(lambda x: x.pk != identifier, self._pending)
            )

            self._pending = filtered_pages

    def check(self, market: str, model: str, pages: Sequence[str]) -> Sequence[str]:
        """Return the list of pages that are localised in the storage folder

        Args:
            market (str): Name of the market being crawled
            model (str): Name of the model in where the pages must be stored
            pages (Sequence[str]): list of identifiers for the pages

        Returns:
            Sequence[str]: List of pages found in the storage
        """
        local = os.path.join(VOLUME, "markets", market, model)

        if not local:
            os.makedirs(local)

        files = [name for _, _, files in os.walk(local) for name in files]
        found = [page for page in pages if page in files]
        return found
