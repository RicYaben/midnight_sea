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

"""Package that provides methods to interact with the persistent volume"""

import os
import glob
import time
import uuid
import zipfile

from dataclasses import dataclass
from lib.logger.logger import log


@dataclass
class Volume:
    """Manager of the Persistent Volume

    Attributes:
        _VOLUME_PATH: path to the volume
        _PENDING: path to the pending files in the volume
        _PARSED: path to the parsed files in the volume
        _ZIP_MAX_FILES: maximum amount of files included in the zip file
    """

    _pending: str = os.path.join("dist", "pending")
    _parsed: str = os.path.join("dist", "parsed")
    _ZIP_MAX_FILES: int = 1000
    _ZIP: str = "*.zip"

    @property
    def pending(self):
        if not os.path.exists(self._pending):
            os.makedirs(self._pending)

        return self._pending

    @property
    def parsed(self):
        if not os.path.exists(self._parsed):
            os.makedirs(self._parsed)

        return self._parsed

    def retrieve(self, name: str) -> bytes:
        """Returns the content of some file

        Args:
            name (str): Name of the file

        Returns:
            bytes: Content of the file
        """
        if name:
            filepath = os.path.join(self.pending, name)

            if os.path.isfile(filepath):
                with open(filepath, "rb") as f:
                    content = f.read()
                    return content

    def store(
        self, data: bytes, name: str = None, market: str = None, page_type: str = None
    ) -> str:
        """Store binary data to a file

        Args:
            data: Byte representation of a file data
            name: String representation of the file name

        Returns:
            str: Name of the file
        """
        if not name:
            name = str(uuid.uuid4())
            name += "".join("_" + n for n in [market, page_type] if n)

        filepath = os.path.join(self.pending, name)

        if data:
            with open(filepath, "wb") as f:
                f.write(data)
                return name

    def compress(
        self,
        name: str,
        zip_filepath: str = None,
        market: str = None,
        page_type: str = None,
    ) -> str or None:
        """This method adds a file that has been parsed to a zip file

        Args:
            name: A string representing the name of the parsed file in the pending folder
            zip_filename: Name of the ZIP file to which include the file

        Returns:
            zip_name: ID number of the zip file
        """
        filepath = os.path.join(self.pending, name)

        # Check if the file exists first
        if not os.path.isfile(filepath):
            return

        # If no file name has been provided, check the directory for the latest
        # zip file stored.
        if not zip_filepath:
            zip_filepath: str = self.latest(
                expression=self._ZIP, market=market, page_type=page_type
            )

        with zipfile.ZipFile(zip_filepath, mode="a") as zipfile:
            # Check if the zip file has room to include more files.
            # Otherwise, create a new ID for the file and repeat the process
            if len(zipfile.namelist()) < self._ZIP_MAX_FILES:
                # Write the file into the zip file
                zipfile.write(filepath, name, zipfile.ZIP_DEFLATED)
                zipfile.close()

                # Remove the file from the directory
                os.remove(filepath)

                return zip_filepath
        

        # Create a new UUID to be used as the name of the zip file
        timestamp: str = time.strftime("%Y_%m_%d-%H_%M")
        filename = f"{timestamp}.zip"

        # Create the path to the parsed files and add the market if any
        zip_path = self.parsed

        for i in [market, page_type]:
            if i:
                zip_path = os.path.join(zip_path, i)

        path = os.path.join(zip_path, filename)
        return self.compress(name=name, zip_filepath=path)

    def latest(
        self, expression: str = "*", market: str = None, page_type: str = None
    ) -> str:
        """Returns the last stored zip file in the `parsed` directory.
        If the directory does not contain any, it will return a new

        Args:
            expression: The file expression to match

        Returns:
            latest: A path string to the latest file
        """
        # Create the path to the parsed files
        zip_path = self.parsed

        # If a market is included, add it to the path
        for i in [market, page_type]:
            if i:
                zip_path = os.path.join(zip_path, i)

        # Create the path just in case
        if not os.path.exists(zip_path):
            os.makedirs(zip_path)

        # Get the files
        path = os.path.join(zip_path, expression)
        g = glob.glob(path)
        files: list = list(filter(os.path.isfile, g))

        # Sort the files by the time created
        files.sort(key=lambda x: os.path.getmtime(x))

        # Get the last zip file if any, otherwise create the file
        if files:
            latest: str = files[-1]
        else:
            # Name the file after the current date
            filename: str = time.strftime("%Y_%m_%d-%H_%M")
            latest: str = os.path.join(zip_path, f"{filename}.zip")

        return latest

    def combine(self):
        """This method combines the zip files into a single one"""
        path = os.path.join(self.parsed, self._ZIP)
        g = glob.glob(path)
        files: list = list(filter(os.path.isfile, g))

        ogname = files.pop(0)
        with zipfile.ZipFile(ogname, "a") as og:
            for file in files:
                with zipfile.ZipFile(file, "r") as f:
                    for n in f.namelist():
                        data = f.open(n)
                        og.writestr(n, data.read())

        return ogname

    def extract(self, market: str = None, keep_zip: bool = True, page_type: str = None):
        """Method to extract the content of zip files"""
        # Get the path to the parsed files
        filepath = self.parsed

        # If a market or page type is included, extend the path
        for i in [market, page_type]:
            if i:
                filepath = os.path.join(filepath, i)

        # Get only zip files
        filepath = os.path.join(filepath, self._ZIP)

        # Get all the zip files
        zip_files = glob.glob(filepath)
        log.info(f"Extracting from {len(zip_files)} Zip files...")

        # Iterate the files
        for e, zip_file in enumerate(zip_files):
            log.info(f"{e}/{len(zip_files)}")
            # Load the file and extract
            with zipfile.ZipFile(zip_file, "r") as f:
                f.extractall(self.pending)

            # If it is not set, delete the zip file
            if not keep_zip:
                os.remove(zip_file)

        log.info("Finished extracting.")

    def delete(self, filename: str):
        fpath = os.path.join(self.pending, filename)

        if os.path.isfile(fpath):
            os.remove(fpath)


# Declare an instance of the volume
volume: Volume = Volume()
