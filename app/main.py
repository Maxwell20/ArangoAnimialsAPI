__author__ = "Maxwell Twente"
__copyright__ = ""
__credits__ = ["Maxwell Twente, "]
__license__ = ""
__version__ = ""
__maintainer__ = "Maxwell Twente"
__email__ = "mtwente@colsa.com"
__status__ = "development"
#UNCLASSIFIED
"""
file@main.py
API Endpoints, support functions and main entry point for the API.
"""
from fastapi import FastAPI
from arango_auth import *
from db_manager import *
import uvicorn 
from config_loader import *
import logging
import logging.config 
import yaml
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend's domain(s) for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    log = logging.getLogger(__name__)
    log.critical('call get http' )
    return {"message": "Hello World"}

@app.get("/get_document_by_key")
async def get_document_by_key(key:str,
                              includeEdges:bool):
    """
    Retrieve an item by key.

    Args:

        key: The datbase key of the item to retrieve.

    Returns:

        dict: documents, connected_documents
    """
    docs = database_manager.get_document_by_key(key, includeEdges)
    return docs

@app.get("/get_document_by_id")
async def get_document_by_key(id:str,
                              includeEdges:bool):
    """
    Retrieve an item by ID.

    Args:

        id: The ID of the item to retrieve.

    Returns:

        dict: documents, connected_documents
    """
    #gets a single document and its connection by id
    docs = database_manager.get_document_by_id(id, includeEdges)
    return docs

@app.get("/get_collection_names")
async def get_collection_names():
    """
    Retrieve collection names in the database.

    Args:

        none

    Returns:

        dict: collection_names, edge_collection_names
    """
    return database_manager.get_collection_names()


#example only remove later
@app.get("/get_recent")
async def get_recent(hours_ago:int):
    """
    Retrieves recent documents.

    Args:

        int: hours_ago 

    Returns:

        dict: documents
    """
    docs = database_manager.get_recent_documents(hoursAgo = 0 )
    return docs

#index of collections and corresponding edge collections must match
@app.get("/get_documents")
async def get_documents(  collections: str,
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
                        edgeCollections:str | None = "",
                        excludeEdges:bool | None = "",
                        collectionFilter:str | None = ""
                        ):
    """
    Retrieves filterd search of specified collections, documents.

    Args:

        collections: str: comma separated list of collections to search

        (optional) startTime: str: time range start

        (optional) endTime: str: time range end

        (optional) longStart: int: longitude range start

        (optional) longEnd: int: longitude range end

        (optional) latStart: int: latitude range start

        (optional) latEnd: latitude range end

        (optional) country: str: only include this country in results

        (optional) type: str: only include this type in results

        (optional) attribute1Start: float: atrribute 1 start range
        
        (optional) attribute1End: float: atrribute 1 end range

        (optional) attribute2Start: float: atrribute 2 start range

        (optional) attribute2End: float: atrribute 2 end range

        (optional) edgeCollections: comma separated list of edge collections to search note: must match in order of collections list

        (optional) excludeEdges: bool: only return documents without edge connections if true default false

        (optional) collectionFilter: str: comma separated list of collections to include in connections excludes all others

    Returns:

        dict: documents, edges, connectedDocuments
        or
        dict: documents
    """
    collections = collections.split(",")
    collectionFilter = collectionFilter.split(",")
    edgeCollections = edgeCollections.split(",")

    
    docs = database_manager.get_specified_documents(collections, startTime, endTime, longStart, longEnd , latStart, latEnd, country, type, attribute1Start, attribute1End, attribute2Start, attribute2End, edgeCollections, excludeEdges, collectionFilter)

    return docs

#index of collections and corresponding edge collections must match
@app.get("/get_documents_paged")
async def get_documents_paged(  collections: str,
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
                        edgeCollections:str | None = "",
                        excludeEdges:bool | None = "",
                        collectionFilter:str | None = ""
                        ):
    """
    Retrieves filterd search of specified collections, documents.

    Args:

        collections: str: comma separated list of collections to search

        pageSize: int: amount of results for a page to include

        pageNumber: index of page to return

        (optional) startTime: str: time range start

        (optional) endTime: str: time range end

        (optional) longStart: int: longitude range start

        (optional) longEnd: int: longitude range end

        (optional) latStart: int: latitude range start

        (optional) latEnd: latitude range end

        (optional) country: str: only include this country in results

        (optional) type: str: only include this type in results

        (optional) attribute1Start: float: atrribute 1 start range

        (optional) attribute1End: float: atrribute 1 end range

        (optional) attribute2Start: float: atrribute 2 start range

        (optional) attribute2End: float: atrribute 2 end range

        (optional) edgeCollections: comma separated list of edge collections to search note: must match in order of collections list

        (optional) excludeEdges: bool: only return documents without edge connections if true default false

        (optional) collectionFilter: str: comma separated list of collections to include in connections excludes all others
        
    Returns:

        dict: documents, edges, connectedDocuments
        or
        dict: documents
    """
    collections = collections.split(",")
    collectionFilter = collectionFilter.split(",")
    edgeCollections = edgeCollections.split(",")
    
    docs = database_manager.get_specified_documents_pages(collections, pageSize, pageNumber, startTime, endTime, longStart, longEnd , latStart, latEnd, country, type, attribute1Start, attribute1End, attribute2Start, attribute2End, edgeCollections, excludeEdges, collectionFilter)

    return docs

@app.get("/get_search_all_paged")
async def get_search_all_paged( 
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
                        includeEdges:bool | None = ""
                        ):
    """
    Retrieves filterd search of all collections, documents.

    Args:

        pageSize: int: amount of results for a page to include

        pageNumber: index of page to return

        (optional) startTime: str: time range start

        (optional) endTime: str: time range end

        (optional) longStart: int: longitude range start

        (optional) longEnd: int: longitude range end

        (optional) latStart: int: latitude range start

        (optional) latEnd: latitude range end

        (optional) country: str: only include this country in results

        (optional) type: str: only include this type in results

        (optional) attribute1Start: float: atrribute 1 start range

        (optional) attribute1End: float: atrribute 1 end range

        (optional) attribute2Start: float: atrribute 2 start range

        (optional) attribute2End: float: atrribute 2 end range

        (optional) includeEdges: true to include edges and connected docs

    Returns:

        dict: documents, edges, connectedDocuments
        or
        dict: documents
    """
    
    docs = database_manager.search_all_collections_paged(pageSize, pageNumber, startTime, endTime, longStart, longEnd , latStart, latEnd, country, type, attribute1Start, attribute1End, attribute2Start, attribute2End, includeEdges)

    return docs

@app.get("/get_search_all")
async def get_search_all( 
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
                        includeEdges:bool | None = ""
                        ):
    """
    Retrieves filterd search of all collections, documents.

    Args:

        (optional) startTime: str: time range start

        (optional) endTime: str: time range end

        (optional) longStart: int: longitude range start

        (optional) longEnd: int: longitude range end

        (optional) latStart: int: latitude range start

        (optional) latEnd: latitude range end

        (optional) country: str: only include this country in results

        (optional) type: str: only include this type in results

        (optional) attribute1Start: float: atrribute 1 start range

        (optional) attribute1End: float: atrribute 1 end range

        (optional) attribute2Start: float: atrribute 2 start range

        (optional) attribute2End: float: atrribute 2 end range
        
        (optional) includeEdges: true to include edges and connected docs

    Returns:

        dict: documents, edges, connectedDocuments
        or
        dict: documents
    """
                        
    
    docs = database_manager.search_all_collections(startTime, endTime, longStart, longEnd , latStart, latEnd, country, type, attribute1Start, attribute1End, attribute2Start, attribute2End, includeEdges)

    return docs

def authenticate_to_db():
    global database_manager
    credentials = ArangoCredentialsEnvironmentVarLoader().build_credentials()
    config = UvicornConfigEnvironmentVarLoader().build_config()
    database_manager = ArangoDatabaseManager(
        database_name = credentials.database,
        username = credentials.username,
        password = credentials.password,
        host = credentials.host
    )
    return config


if __name__ == '__main__':
    #start from main: python main.py
    config = authenticate_to_db()
    
    with open(config.log_config, 'r') as stream: 
        logConfig = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(logConfig)


    log = logging.getLogger(__name__)
      
    log.debug('Accepted signing CAs for client cert %s' , config.ssl_ca_certs)
    log.debug('Server https cert %s' , config.ssl_keyfile)
    log.debug('Server https private key %s' , config.ssl_certfile)
    log.debug('logging config file %s' , config.log_config)
    uvicorn.run(app, host=config.host, port=int(config.port), ssl_ca_certs=config.ssl_ca_certs, ssl_cert_reqs=int(config.ssl_cert_reqs), ssl_keyfile=config.ssl_keyfile, ssl_certfile=config.ssl_certfile, log_config=config.log_config)
    

#UNCLASSIFIED
 