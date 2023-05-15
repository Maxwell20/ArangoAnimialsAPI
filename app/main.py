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
from arango_auth import *
from db_manager import *
import uvicorn 
from config_loader import *
import logging
import logging.config 
import yaml
from logger import *

app = FastAPI()

@app.get("/")
async def root():
    log = logging.getLogger(__name__)
    log.critical('call get http' )
    return {"message": "Hello World"}

@app.get("/get_collection_names")
async def get_collection_names():
   return database_manager.get_collection_names()


#example only remove later
@app.get("/get_recent")
async def get_recent(hours_ago:int,
                     collections:str):
    docs = database_manager.get_recent_documents(collections, hoursAgo = 0 )
    return docs

@app.get("/get_animals")
async def get_animals(  collections: str,
                        startTime: str  | None = "",
                        endTime: str | None = "",
                        longStart: float | None = "",
                        longEnd: float | None = "",
                        latStart: float | None = "", 
                        latEnd: float | None = "", 
                        country:str | None = "",
                        type:str | None = "",
                        attribute1Start:float | None = "",
                        attribute1End:float | None = "",
                        attribute2Start:float | None = "",
                        attribute2End:float | None = "",
                        includeEdges:bool | None = "",
                        edgeCollection:str | None = "",
                        excludeEdges:bool | None = "",
                        collecitonFilter:str | None = ""
                        ):
    collections = collections.split(",")
    collecitonFilter = collecitonFilter.split(",")
    
    docs = database_manager.get_specified_documents(collections, startTime, endTime, longStart, longEnd , latStart, latEnd, country, type, attribute1Start, attribute1End, attribute2Start, attribute2End, includeEdges, edgeCollection, excludeEdges, collecitonFilter)

    return docs

@app.get("/get_animals_pages")
async def get_animals_pages(  collections: str,
                        pageSize:int ,
                        pageNumber:int,
                        startTime: str  | None = "",
                        endTime: str | None = "",
                        longStart: float | None = "",
                        longEnd: float | None = "",
                        latStart: float | None = "", 
                        latEnd: float | None = "", 
                        country:str | None = "",
                        type:str | None = "",
                        attribute1Start:float | None = "",
                        attribute1End:float | None = "",
                        attribute2Start:float | None = "",
                        attribute2End:float | None = "",
                        includeEdges:bool | None = "",
                        edgeCollection:str | None = "",
                        excludeEdges:bool | None = "",
                        collecitonFilter:str | None = ""
                        ):
    collections = collections.split(",")
    collecitonFilter = collecitonFilter.split(",")
    
    docs = database_manager.get_specified_documents_pages(collections, pageSize, pageNumber, startTime, endTime, longStart, longEnd , latStart, latEnd, country, type, attribute1Start, attribute1End, attribute2Start, attribute2End, includeEdges, edgeCollection, excludeEdges, collecitonFilter)

    return docs

def authenticate_to_db():
    global credentials, database_manager
    credentials = ArangoCredentialsEnvironmentVarLoader().build_credentials()
    config = UvicornConfigEnvironmentVarLoader().build_config()
    database_manager = ArangoDatabaseManager(
        database_name = credentials.database,
        username = credentials.username,
        password = credentials.password,
        host = credentials.host
    )


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
    
    with open(config.log_config, 'r') as stream: 
        logConfig = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(logConfig)

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
 