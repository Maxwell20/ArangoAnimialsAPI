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
"""
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
from logger import Logger

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
                              includeEdges:bool,
                              edgeCollection:str | None = ""):
    #gets a single document and its connection by key
    docs = database_manager.get_document_by_key(key,includeEdges, edgeCollection)

@app.get("/get_collection_names")
async def get_collection_names():
   return database_manager.get_collection_names()


#example only remove later
@app.get("/get_recent")
async def get_recent(hours_ago:int,
                     collections:str):
    docs = database_manager.get_recent_documents(collections, hoursAgo = 0 )
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
                        includeEdges:bool | None = "",
                        edgeCollections:str | None = "",
                        excludeEdges:bool | None = "",
                        collecitonFilter:str | None = ""
                        ):
    collections = collections.split(",")
    collecitonFilter = collecitonFilter.split(",")
    edgeCollections = edgeCollections.split(",")

    
    docs = database_manager.get_specified_documents(collections, startTime, endTime, longStart, longEnd , latStart, latEnd, country, type, attribute1Start, attribute1End, attribute2Start, attribute2End, includeEdges, edgeCollection, excludeEdges, collecitonFilter)

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
                        includeEdges:bool | None = "",
                        edgeCollections:str | None = "",
                        excludeEdges:bool | None = "",
                        collecitonFilter:str | None = ""
                        ):
    collections = collections.split(",")
    collecitonFilter = collecitonFilter.split(",")
    edgeCollections = edgeCollections.split(",")
    
    docs = database_manager.get_specified_documents_pages(collections, pageSize, pageNumber, startTime, endTime, longStart, longEnd , latStart, latEnd, country, type, attribute1Start, attribute1End, attribute2Start, attribute2End, includeEdges, edgeCollection, excludeEdges, collecitonFilter)

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

    uvicorn.run(app, host=config.host, port=int(config.port), ssl_ca_certs=config.ssl_ca_certs, ssl_cert_reqs=int(config.ssl_cert_reqs), ssl_keyfile=config.ssl_keyfile, ssl_certfile=config.ssl_certfile, log_config=config.log_config)
    
    print("this is a test")
 
    log = logging.getLogger(__name__)
    log.critical('call get http' )
    log = logging.getLogger(__name__)
    log.warning('This is a warning message from logger')
    log.error('This is an error message from logger')
    log.critical('This is a critical message from logger')
    log.info("testinfo")
      
    log.debug('Accepted signing CAs for client cert %s' , config.ssl_ca_certs)
    log.debug('Server https cert %s' , config.ssl_keyfile)
    log.debug('Server https private key %s' , config.ssl_certfile)
    log.debug('logging config file %s' , config.log_config)
#UNCLASSIFIED
 