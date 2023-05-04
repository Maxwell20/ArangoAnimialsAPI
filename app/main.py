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
from arango_auth import *
# from .arango_auth import  ArangoCredentials, ArangoCredentialsEnvironmentVarLoader
from db_manager import *
import uvicorn 
from config_loader import *
import logging


app = FastAPI()

@app.get("/")
async def root():
    log = logging.getLogger(__name__)
    log.critical('call get http' )
    return {"message": "Hello World"}


#example only remove later
@app.get("/get_recent")
async def get_recent(hours_ago:int | None = None):
    docs = database_manager.get_recent_documents('fauna_sightings', hours_ago= 0 )
    return docs



#TODO: Pass username and password through api
@app.get("/all_animals")
async def all_animals():
    all_docs = database_manager.get_all_documents('fauna_sightings')
    return all_docs

#TODO: Pass username and password through api
@app.get("/get_animals")
async def get_animals(collection: str, startTime: str  | None = None, endTime: str | None = None, long: float | None = None, lat: float | None = None, country:str | None = None, type:str | None = None):
    docs = database_manager.get_specified_documents('fauna_sightings', startTime, endTime, long, lat, country, type)
    return docs

if __name__ == '__main__':
    #start from main: python main.py
    global credentials, database_manager
    credentials = ArangoCredentialsEnvironmentVarLoader().build_credentials()
    config = UvicornConfigEnvironmentVarLoader().build_config()
    database_manager = ArangoDatabaseManager(
        database_name = credentials.database,
        username = credentials.username,
        password = credentials.password,
        host = credentials.host
    )
   
    uvicorn.run(app, host=config.host, port=int(config.port), ssl_ca_certs=config.ssl_ca_certs, ssl_cert_reqs=int(config.ssl_cert_reqs), ssl_keyfile=config.ssl_keyfile, ssl_certfile=config.ssl_certfile, log_config=config.log_config)
    
    log = logging.getLogger(__name__)
    log.warning('This is a warning message from logger')
    log.error('This is an error message from logger')
    log.critical('This is a critical message from logger')
      
    log.debug('Accepted signing CAs for client cert %s' , config.ssl_ca_certs)
    log.debug('Server https cert %s' , config.ssl_keyfile)
    log.debug('Server https private key %s' , config.ssl_certfile)
    log.debug('logging config file %s' , config.log_config)
#UNCLASSIFIED
 