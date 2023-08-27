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

"""This package contains multiple observable wrapper events"""

import os
from typing import Any, Dict

from sqlalchemy import or_
from sqlalchemy.orm.collections import InstrumentedList
from storage.database.api import (
    ApiFactory,
    ItemEndpoint,
    PageEndpoint,
    VendorEndpoint,
)
from storage.volume.volume import volume

from lib.logger import logger

def get_pending_pages(market: str = None, limit: int = 100):
    """Returns a list of pending to scrape pages"""
    page_ep = PageEndpoint()

    pending = (
        # Query the model
        page_ep.db.session.query(page_ep.model)
        # Filter the db to get those without vendor or items
        .filter(
            page_ep.model.vendor == None,  # There isnt a vendor
            page_ep.model.item == None,  # There isnt an item
            page_ep.model.file.is_not(None),  # There is a file
        )
    )

    if market:
        pending = pending.filter(page_ep.model.market.has(name=market))

    ret = pending.limit(limit).all()
    return ret


def get_vendors_without_page():
    """Returns a list of vendors without a page assigned"""
    vendor_ep = VendorEndpoint()

    vendors = (
        # Query the model
        vendor_ep.db.session.query(vendor_ep.model)
        # Filther the db to get those without page but containing a path
        .filter(
            vendor_ep.model.page == None,  # The isnt a page
            vendor_ep.model.path.is_not(None),  # There is a path
        )
        # Get all the vendors from the query
        .all()
    )

    return vendors


def get_vendors_feedback(market: str = None):
    """Returns a list of vendors"""
    vendor_ep = VendorEndpoint()

    vendors = (
        # Query the model
        vendor_ep.db.session.query(vendor_ep.model)
    )

    if market:
        vendors = vendors.filter(vendor_ep.model.page.market.has(name=market))

    return vendors.all()


def get_page_content(page):
    """Returns the content from some file stored in the volume"""
    ret = volume.retrieve(page.file)
    return ret


def scrape_content(page, data: bytes, scraper) -> Dict[Any, Any]:
    """Scrapes the data points from some content

    Args:
        page (Page): Page instance
        data (bytes): Content of the file

    Returns:
        Dict[Any, Any]: Data points found in the file
    """
    # Get the market and model from the page
    if page.market:
        market = page.market.name
        model = page.page_type

        # Send the content to scrape
        data_points = scraper.scrape(market=market, model=model, data=data)
        return data_points


def store_serialised_entry(model: str, data: Dict[Any, Any], force: bool = True):
    """Stores some entry serialised data

    Args:
        model (str): Name of the model. In lower case
        data (Dict[Any, Any]): Data with which to fill the entry
        force (bool, optional): Force the creation of the entry to a new one. Defaults to True.
    """
    # Clean the model
    model = model.lower()

    endpoint = ApiFactory.get_endpoint(model)
    instance = endpoint.store(force=force, **data)

    return instance


def scrape(scraper, market: str = None):
    """Wrapper for the events related to scraping content from pending files"""
    # Get the pending pages
    logger.info("Scraping pending content")
    pending = get_pending_pages(market=market)

    while pending:
        print(f"Pages: {len(pending)}")

        for page in pending:
            # Get the content
            content = get_page_content(page)

            if not content:
                # Update the page to let know that the file could
                # not be found
                page_ep = PageEndpoint()
                page_ep.update(page, file=None)

                continue

            # Store the content on the respective model
            data_points = scrape_content(page, content, scraper=scraper)

            if not data_points:
                # If the page could not be parsed, delete it from the database, it might contain errors.
                page_ep = PageEndpoint()
                page_ep.delete(page)

                continue

            data_points.update({"page": {"id": page.id}})

            # Store the data in the database serialised
            _ = store_serialised_entry(model=page.page_type.value, data=data_points)

            # Compress the page, as it will not be needed anymore
            volume.compress(
                name=page.file,
                market=page.market.name,
                page_type=page.page_type.code,
            )

        pending = get_pending_pages(market=market)


def get_market_pages(market: str = None, pending: list = None):
    page_ep = PageEndpoint()

    pages = (
        # Query the model
        page_ep.db.session.query(page_ep.model).filter(
            or_(
                page_ep.model.item != None, page_ep.model.vendor != None
            ),  # There is an item or a vendor
            page_ep.model.file.is_not(None),  # There is a file
        )
    )

    if pending:
        pages = pages.filter(page_ep.model.file.in_(pending))

    if market:
        pages = pages.filter(page_ep.model.market.has(name=market))

    ret = pages.all()
    return ret


def get_pending_files():
    filenames = next(os.walk(volume.pending), (None, None, []))[2]
    return filenames


def rescrape_targetted(scraper, market: str):
    """Wrapper for the events related to re-scrape the content of the pages"""
    eps = {"item": ItemEndpoint(), "vendor": VendorEndpoint()}
    pending = get_pending_files()
    logger.info(f"Rescraping... pending: {len(pending)}")

    csize = 100
    for i in range(0, len(pending), csize):
        chunk = pending[i : i + csize]
        pages = get_market_pages(market=market, pending=chunk)

        for page in pages:
            # Get the content
            content = get_page_content(page)

            if not content:
                continue

            # Store the content on the respective model
            data_points = scrape_content(page, content, scraper=scraper)
            ep = eps[page.page_type.code]

            if not data_points:
                # Delete the file
                volume.delete(page.file)
                # Empty the space
                pe = PageEndpoint()
                pe.update(page, file=None)

                continue

            # Store the data in the database serialised
            instance = getattr(page, page.page_type.code)
            if isinstance(instance, InstrumentedList):
                instance = instance[0]

            # Update the instance with the data points
            ep.update(instance, **data_points)

            # Compress the page, as it will not be needed anymore
            volume.compress(
                name=page.file, market=market, page_type=page.page_type.code
            )


def re_scrape(
    scraper, market: str, page_type: str, extract: bool = True, keep_zip=True
):
    # Extract the content if stated
    if extract:
        volume.extract(market=market, keep_zip=keep_zip, page_type=page_type)

    # Scrape the targetted content
    rescrape_targetted(scraper, market=market)


def create_pending_vendors():
    """This method collects the vendors that do no have a page assigned yet but contain a path.
    Then, a page is created using the path and set to `pending` for crawling.
    """
    # Get the list of vendors without page but with a path
    vendors_without_page = get_vendors_without_page()
    page_ep = PageEndpoint()

    for vendor in vendors_without_page:
        
        items = vendor.items
        if not items:
            continue

        market = (items[0].page.market.name,)
        # Semi-serialise the data into a json like object
        serialised: dict = {
            "url": vendor.path,
            "market": {
                "name": market,
            },
            "page_type": "vendor",
        }

        # Attempt to find the page. If so, jump to the next
        instance = page_ep.find(url=vendor.path, market=market)
        if instance:
            continue

        # Create the instance and store the page info
        # NOTE: This will make that when the market is crawled next, it will crawl these vendors
        instance = page_ep.store(force=False, **serialised)

        # Update the page with the vendor and save
        instance.vendor = vendor
        instance.save()


def reputation_fn(
    negative: float = None, total: float = None, disputes: float = None, *args, **kwargs
) -> float or None:
    # Get the percentage of the positives and disputes

    if negative and total:
        prc = 1 - (negative / total)

        if not disputes:
            return prc
        
        disputes_prc = 1 - (disputes / total)
        prc = prc * disputes_prc
        return prc


def calcualte_reputation(market: str = None):
    """Function to calculate the reputation of the vendors"""
    ep = VendorEndpoint()

    # Get the vendors
    vendors = get_vendors_feedback(market=market)

    for vendor in vendors:
        reputation = reputation_fn(
            negative=vendor.negative_fb,
            total=vendor.total_fb,
            disputes=vendor.disputes_fb,
        )

        if reputation:
            ep.update(vendor, reputation=reputation)
