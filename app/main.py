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
from fastapi import FastAPI, APIRouter
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
origins = ["https://www.localhostdomain.com/","https://localhost", "https://exo-fast-api/","http://www.localhostdomain.com/","http://localhost", "http://exo-fast-api/"]

router = APIRouter(prefix="/rest")
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #origins # ["*"] # Replace ["*"] with your frontend's domain(s) for production <origins>
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/rest")
app.include_router(router)


@router.get("/")
async def root():
    log = logging.getLogger(__name__)
    log.critical('call get http' )
    return {"message": "Hello World"}

@router.get("/get_document_by_key")
async def get_document_by_key(key:str,
                              includeEdges:bool,
                              edgeCollection:str | None = ""):
    #gets a single document and its connection by key
    docs = database_manager.get_document_by_key(key,includeEdges, edgeCollection)
    return docs

@router.get("/get_collection_names")
async def get_collection_names():
   return database_manager.get_collection_names()


#example only remove later
@router.get("/get_recent")
async def get_recent(hours_ago:int,
                     collections:str):
    docs = database_manager.get_recent_documents(collections, hoursAgo = 0 )
    return docs

#index of collections and corresponding edge collections must match
@router.get("/get_documents")
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
                        collectionFilter:str | None = ""
                        ):
    collections = collections.split(",")
    collectionFilter = collectionFilter.split(",")
    edgeCollections = edgeCollections.split(",")

    
    docs = database_manager.get_specified_documents(collections, startTime, endTime, longStart, longEnd , latStart, latEnd, country, type, attribute1Start, attribute1End, attribute2Start, attribute2End, includeEdges, edgeCollections, excludeEdges, collectionFilter)

    return docs

#index of collections and corresponding edge collections must match
@router.get("/get_documents_paged")
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
                        collectionFilter:str | None = ""
                        ):
    collections = collections.split(",")
    collectionFilter = collectionFilter.split(",")
    edgeCollections = edgeCollections.split(",")
    
    docs = database_manager.get_specified_documents_pages(collections, pageSize, pageNumber, startTime, endTime, longStart, longEnd , latStart, latEnd, country, type, attribute1Start, attribute1End, attribute2Start, attribute2End, includeEdges, edgeCollections, excludeEdges, collectionFilter)

    return docs

def init_authenticate_to_db():
    global database_manager
    credentials = ArangoCredentialsEnvironmentVarLoader().build_credentials()
    database_manager = ArangoDatabaseManager(
        database_name = credentials.database,
        username = credentials.username,
        password = credentials.password,
        host = credentials.host
    )
    return database_manager


if __name__ == '__main__':
    #start from main: python main.py
    global database_manager
    global app_server_config
    database_manager = init_authenticate_to_db()
    app_server_config = UvicornConfigEnvironmentVarLoader().build_config()
    # server is not configured yet so logger is also not configured.
    with open(app_server_config.log_config_file, 'r') as stream: 
        log_config_file = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(log_config_file)
    log = logging.getLogger(__name__)
    
    time.sleep(5)
    # log.warning('This is a warning message from logger %s' , "hi")
    # log.error('This is an error message from logger %s' , "hi")
    # log.critical('This is a critical message from logger %s' , "hi")
    
    log.debug('Proxy is %s' , app_server_config.reverse_proxy_on)
    if bool("true" == app_server_config.reverse_proxy_on.lower()) :
        uvicorn.run(router, host=app_server_config.host, port=int(app_server_config.port), log_config=app_server_config.log_config_file)
    else :    
        log.debug('Accepted signing CAs for client cert %s' , app_server_config.ssl_ca_certs)
        log.debug('Server https cert %s' , app_server_config.ssl_keyfile)
        log.debug('Server https private key %s' , app_server_config.ssl_certfile)
        log.debug('logging app_server_config file %s' , app_server_config.log_config_file)
        uvicorn.run(router, host=app_server_config.host, port=int(app_server_config.port), ssl_ca_certs=app_server_config.ssl_ca_certs, ssl_cert_reqs=int(app_server_config.ssl_cert_reqs), ssl_keyfile=app_server_config.ssl_keyfile, ssl_certfile=app_server_config.ssl_certfile, log_config=app_server_config.log_config_file)
    

#UNCLASSIFIED
 