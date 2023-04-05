__author__ = "Maxwell Twente"
__copyright__ = ""
__credits__ = ["Maxwell Twente, "]
__license__ = ""
__version__ = ""
__maintainer__ = "Maxwell Twente"
__email__ = "mtwente@colsa.com"
__status__ = "development"
#UNCLASSIFIED
#file@main.py

"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

from fastapi import FastAPI
import json
from .arango_auth import  ArangoCredentials, ArangoCredentialsEnvironmentVarLoader
from .db_manager import ArangoDatabaseManager

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


#example only remove later
@app.get("/users")
async def users():
    users = [
        {
            "name": "Mars Kule",
            "age": 25,
            "city": "Lagos, Nigeria"
        },

        {
            "name": "Mercury Lume",
            "age": 23,
            "city": "Abuja, Nigeria"
        },

         {
            "name": "Jupiter Dume",
            "age": 30,
            "city": "Kaduna, Nigeria"
        }
    ]

    return users

#TODO: Pass username and password through api
@app.get("/all_animals")
async def all_animals():
# async def all_animals(user: str, pwd: str | None = None):

    # credentials = ArangoCredentialsEnvironmentVarLoader().build_credentials()
    database_manager = ArangoDatabaseManager(
        database_name = "SightingsDatabase",
        username = 'root',
        password = 'adbpwd',
        host = "http://localhost:1234/"
    )

    all_docs = database_manager.get_all_documents('fauna_sightings')
    return all_docs

#TODO: Pass username and password through api
@app.get("/get_animals")
async def get_animals(collection: str, startTime: str  | None = None, endTime: str | None = None, long: float | None = None, lat: float | None = None, country:str | None = None, type:str | None = None):

    # credentials = ArangoCredentialsEnvironmentVarLoader().build_credentials()
    database_manager = ArangoDatabaseManager(
        database_name = "SightingsDatabase",
        username = 'root',
        password = 'adbpwd',
        host = "http://localhost:1234/"
    )

    docs = database_manager.get_specified_documents('fauna_sightings', startTime, endTime, long, lat, country, type)
    return docs
#UNCLASSIFIED
