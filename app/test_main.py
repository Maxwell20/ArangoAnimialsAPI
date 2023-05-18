__author__ = "Maxwell Twente"
__copyright__ = ""
__credits__ = ["Maxwell Twente, "]
__license__ = ""
__version__ = ""
__maintainer__ = "Maxwell Twente"
__email__ = "mtwente@colsa.com"
__status__ = "development"
#UNCLASSIFIED
#file@test_main.py
"""
    purpose: unit test for api 
"""

from fastapi.testclient import TestClient
from main import app, authenticate_to_db
import os

client = TestClient(app)

def test_read_main():
    print("test main")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_get_documents():
    print("testing time range query")
    os.environ["ARANGO_HOST"] = "http://localhost:1234/"
    os.environ["ARANGO_DATABASE"] ="SightingsDatabase"
    os.environ["ARANGO_USERNAME"] ="root"
    os.environ["ARANGO_PASSWORD"] ="adbpwd"
    os.environ["UVICORN_HOST"] ="0.0.0.0"
    os.environ["UVICORN_PORT"] ="443"
    authenticate_to_db()
    response = client.get("/get_documents?collections=sightings&startTime=2018-07-11T12%3A50%3A40&endTime=2018-07-12T12%3A50%3A40")
    assert response.status_code == 200
    print(response.content)
    assert response.content == b'[{"doc":{"_key":"50g7a3g8b9d07583","_id":"sightings/50g7a3g8b9d07583","_rev":"_f3sYomG--A","country":"NorthTemperateZone","longitude":-22.638144419683705,"true_sighting_id":"984de599b1625e2f","timestamp":"2018-07-11T12:50:40","latitude":54.989758481673206,"species":"RadioactiveWeasel"},"edges":[]},{"doc":{"_key":"17e79da93312140f","_id":"sightings/17e79da93312140f","_rev":"_f3sYoma-_e","country":"NorthZone","longitude":-135.83006102266216,"true_sighting_id":"3048dbg806g1d87e","timestamp":"2018-07-12T10:36:39","latitude":72.88765868577106,"species":"PolarBear"},"edges":[]},{"doc":{"_key":"e0g5845d963f8cbd","_id":"sightings/e0g5845d963f8cbd","_rev":"_f3sYooi-_T","country":"NorthTemperateZone","longitude":-18.374000132500367,"true_sighting_id":"5g7c3afge8e2ef06","timestamp":"2018-07-11T14:39:30","latitude":46.82536179305713,"species":"RadioactiveWeasel"},"edges":[]}]'


#UNCLASSIFIED
