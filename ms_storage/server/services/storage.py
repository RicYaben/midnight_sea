from ms_storage.server.interfaces import Service, ServiceFactory
from ms_storage.database.api import (
    PageEndpoint,
)

from ms_storage.volume.volume import volume

# Although the name is confusing, this refers to the server/client connection between
# the crawler and the storage services
from ms_storage.protos import storage_pb2_grpc
from ms_storage.protos import storage_pb2


@ServiceFactory.register("Storage")
class Storage(storage_pb2_grpc.StorageServicer, Service):
    """Endpoint for the Storage functions"""

    def Store(self, request, context) -> storage_pb2.StoreResponse:
        """This function offers an endpoint to store PAGES in the database"""
        fc = PageEndpoint()

        for page in request.pages:
            if page.url:
                # Semi-serialise the data into a json like object
                serialised: dict = {
                    "url": page.url,
                    "market": {
                        "name": request.market,
                    },
                    "page_type": request.model,
                    # "status_code": page.status_code,
                }

                if page.data:
                    # Store the content of the page in the local storage
                    filename = volume.store(data=page.data, market=request.market, page_type=request.model)
                    serialised.update({"file": filename})

                # Attempt to find the page
                instance = fc.find(url=page.url, market=request.market)

                if instance:
                    fc.update(instance, **serialised)
                else:
                    fc.store(force=False, **serialised)

        response = storage_pb2.StoreResponse(market=request.market, model=request.model)

        return response

    def Pending(self, request, context) -> storage_pb2.PendingResponse:
        """Returns the list of page urls that have not been crawled yet."""
        fc = PageEndpoint()

        # Get the PENDING pages from the dabatase. These are the ones that do not have any
        # file attached to it
        pages = fc.pending(market=request.market, page_type=request.model)

        # Get only the urls from the pages
        pending = [page.url for page in pages if page.url]

        return storage_pb2.PendingResponse(
            pages=pending, market=request.market, model=request.model
        )

    def Check(self, request, context):
        """Returns the list of pages that can be found in the database"""
        fc = PageEndpoint()

        # Get the existing pages from the db and create placeholders for those which are not
        pages = fc.exists(
            market=request.market,
            page_type=request.model,
            pages=request.pages,
            placeholders=True,
        )

        # Get only the urls from the pages
        exists = [page.url for page in pages if page.url]

        return storage_pb2.CheckResponse(
            pages=exists, market=request.market, model=request.model
        )
