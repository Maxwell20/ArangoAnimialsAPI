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
file@test_main.py
Unit test for api endpoints
We test mostly just for the api to return OK
in this since test_db_manager.py has 
test for the database calls already
"""

from fastapi.testclient import TestClient
from main import app, authenticate_to_db, router

client = TestClient(router)
client.base_url += "/rest"
client.base_url = client.base_url.rstrip("/") + "/"

#client = TestClient(app)
def test_read_main():
    authenticate_to_db()
    response = client.get("/")
    assert response.status_code == 200

def test_get_document_by_key():
    authenticate_to_db()
    response = client.get("/get_document_by_key?key=af03d7e9bf1b9d2d&includeEdges=false")
    assert response.status_code == 200
    
def test_get_document_by_id():
    authenticate_to_db()
    response = client.get("/get_document_by_id?id=sightings%2Faf03d7e9bf1b9d2d&includeEdges=false")
    assert response.status_code == 200

def test_get_collection_names():
    authenticate_to_db()
    response = client.get("/get_collection_names")
    assert response.status_code == 200

def test_get_recent():
    authenticate_to_db()
    response = client.get("/rest/get_recent?hours_ago=24")
    assert response.status_code == 200


def test_get_documents():
    authenticate_to_db()
    response = client.get("/get_documents?collections=sightings&startTime=2018-07-11T12%3A50%3A40&endTime=2018-07-12T12%3A50%3A40")
    assert response.status_code == 200
  
def test_get_documents_paged():
    authenticate_to_db()
    response = client.get("/get_documents_paged?collections=sightings&pageSize=10&pageNumber=1")
    assert response.status_code == 200

def test_search_all_paged():
    authenticate_to_db()
    response = client.get("/get_search_all_paged?pageSize=10&pageNumber=1")
    assert response.status_code == 200

def test_search_all():
    authenticate_to_db()
    response = client.get("/get_search_all")
    assert response.status_code == 200

#UNCLASSIFIED
