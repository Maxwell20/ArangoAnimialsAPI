__author__ = "Maxwell Twente"
__copyright__ = ""
__credits__ = ["Maxwell Twente, "]
__license__ = ""
__version__ = ""
__maintainer__ = "Maxwell Twente"
__email__ = "mtwente@colsa.com"
__status__ = "development"


"""
file@test_db_manager.py
Purpose is to provide unit test for the db_manager class
test all the database queries for expected return values
"""

import pytest
from datetime import datetime, timedelta
from db_manager import ArangoDatabaseManager
from arango_auth import *


@pytest.fixture
def DbManager():
     # create an instance of DbManager for testing
    credentials = ArangoCredentialsEnvironmentVarLoader().build_credentials()
    database_manager = ArangoDatabaseManager(
        database_name = credentials.database,
        username = credentials.username,
        password = credentials.password,
        host = credentials.host
    )
    return database_manager

def test_get_document_by_key(DbManager):
    # test case 1: check and see if it returns correct doc
    key = "af03d7e9bf1b9d2d"
    result = DbManager.get_document_by_key(key, False)
    assert result[0][0]["_key"] == key


def test_get_document_by_id(DbManager):
    # test case 1: check and see if it returns correct doc
    id = "sightings/af03d7e9bf1b9d2d"
    result = DbManager.get_document_by_id(id, False)
    assert result[0][0]["_id"] == id

def test_get_recent_documents(DbManager):
    # test case 1: Verify that the function returns a list of documents
    hoursAgo = 24
    result = DbManager.get_recent_documents(hoursAgo)
    assert isinstance(result, list)

    # test case 2: Verify that the returned list contains only recent documents
    # assuming the documents have a timestamp or creation date field
    for document in result:
        assert document.timestamp >= datetime.now() - timedelta(hours=hoursAgo)


def test_get_specified_documents(DbManager):
    # test case 1: Verify that the function returns a list of documents
    collections = ["sightings", "audios"]
    edge_collections = ['edge-sightings', "edge-audios"]
    result = DbManager.get_specified_documents(collections, edgeCollections = edge_collections)
    assert isinstance(result, list)

    # test case 2: Verify that the function handles optional parameters correctly
    startTime = "2021-06-09T13:11:08"
    endTime = "2021-09-09T13:11:08"
    longStart = -22
    longEnd = 10
    latStart = 50
    latEnd = 81
    country = "NorthZone"
    type_ = "RadioactiveWeasel"
    attribute1Start = 0
    attribute1End = 1
    attribute2Start = 0
    attribute2End = 1
    result = DbManager.get_specified_documents(
        collections,
        edgeCollections = edge_collections,
        startTime=startTime,
        endTime=endTime,
        longStart=longStart,
        longEnd=longEnd,
        latStart=latStart,
        latEnd=latEnd,
        country=country,
        type=type_,
        attribute1Start=attribute1Start,
        attribute1End=attribute1End,
        attribute2Start=attribute2Start,
        attribute2End=attribute2End,
    )
    # perform assertions on the result

    # assert that the result is a list
    assert isinstance(result, list)

    # assert that the result is not empty
    assert len(result) > 0

    # assert that each document in the result meets the specified criteria
    for document in result:
        assert document['doc']["timestamp"] >= startTime
        assert document['doc']["timestamp"] <= endTime
        assert document['doc']["longitude"] >= longStart
        assert document['doc']["longitude"] <= longEnd
        assert document['doc']["latitude"] >= latStart
        assert document['doc']["latitude"] <= latEnd
        assert document['doc']["country"] == country
        assert document["doc"]["species"] == type_
        if "attribute1" in document["doc"]:
            assert document["doc"]["attribute1"] >= attribute1Start and document.attribute1 <= attribute1End
        if "attribute2" in document["doc"]:
            assert document["doc"]["attribute2"] >= attribute2Start and document.attribute2 <= attribute2End


    # test case 3: Verify that the function handles other parameters correctly
    # test exclude edges
    edgeCollections = ["edge-sightings"]
    excludeEdges = True
    result = DbManager.get_specified_documents(
        collections,
        edgeCollections=edgeCollections,
        excludeEdges=excludeEdges
        )
    # perform assertions on the result

    # assert that the result is a list
    assert isinstance(result, list)

    # assert that each document has no edges
    assert "connectedDocs" not in result

    # test for only connectected docs from audios
    connectionFilter = ["audios"]
    result = DbManager.get_specified_documents(
        collections,
        edgeCollections=edgeCollections,
        connectionFilter=connectionFilter
    )
    for con in document["connectedDocs"]:
        assert not any(item in con["_id"] for item in connectionFilter)



def test_get_specified_documents_pages(DbManager):
    # test case 1: Verify that the function returns a list of documents
    collections = ["sightings", "audios"]
    edge_collections = ['edge-sightings', "edge-audios"]
    result = DbManager.get_specified_documents_pages(collections, edgeCollections = edge_collections)
    assert isinstance(result, list)

    # test case 2: Verify that the pageSize parameter is working correctly
    pageSize = 20
    result1 = DbManager.get_specified_documents_pages(collections, edgeCollections = edge_collections, pageSize=pageSize)
    assert len(result1) <= pageSize

    # test case 3: Verify that the pageNumber parameter is working correctly
    pageNumber = 2
    result2 = DbManager.get_specified_documents_pages(collections, edgeCollections = edge_collections, pageNumber=pageNumber)
    assert result1 != result2 #Assume page 2 is different

    # test case 4: Verify that the function handles optional parameters correctly
    startTime = "2021-06-09T13:11:08"
    endTime = "2021-09-09T13:11:08"
    longStart = -22
    longEnd = 10
    latStart = 50
    latEnd = 81
    country = "NorthZone"
    type_ = "RadioactiveWeasel"
    attribute1Start = 0
    attribute1End = 1
    attribute2Start = 0
    attribute2End = 1
    pageNumber = 1
    result = DbManager.get_specified_documents_pages(
        collections,
        pageSize,
        pageNumber,
        edgeCollections = edge_collections,
        startTime=startTime,
        endTime=endTime,
        longStart=longStart,
        longEnd=longEnd,
        latStart=latStart,
        latEnd=latEnd,
        country=country,
        type=type_,
        attribute1Start=attribute1Start,
        attribute1End=attribute1End,
        attribute2Start=attribute2Start,
        attribute2End=attribute2End,
    )
    # perform assertions on the result

    # assert that the result is a list
    assert isinstance(result, list)

    # assert that the result is not empty
    assert len(result) > 0

    # assert that each document in the result meets the specified criteria
    for document in result:
        assert document['doc']["timestamp"] >= startTime
        assert document['doc']["timestamp"] <= endTime
        assert document['doc']["longitude"] >= longStart
        assert document['doc']["longitude"] <= longEnd
        assert document['doc']["latitude"] >= latStart
        assert document['doc']["latitude"] <= latEnd
        assert document['doc']["country"] == country
        assert document["doc"]["species"] == type_
        if "attribute1" in document["doc"]:
            assert document["doc"]["attribute1"] >= attribute1Start and document.attribute1 <= attribute1End
        if "attribute2" in document["doc"]:
            assert document["doc"]["attribute2"] >= attribute2Start and document.attribute2 <= attribute2End


    # test case 5: Verify that the function handles other parameters correctly
    # test exclude edges
    # exclude items from edge audios
    edgeCollections = ["edge-sightings"]
    excludeEdges = True
    result = DbManager.get_specified_documents_pages(
        collections,
        pageSize,
        pageNumber,
        edgeCollections=edgeCollections,
        excludeEdges=excludeEdges
        )
    # perform assertions on the result

    # assert that the result is a list
    assert isinstance(result, list)

    # test for only connectected docs from audios
    connectionFilter = ["audios"]
    result = DbManager.get_specified_documents_pages(
        collections,
        pageSize,
        pageNumber,
        edgeCollections=edgeCollections,
        connectionFilter=connectionFilter
    )
    for con in document["connectedDocs"]:
        assert not any(item in con["_id"] for item in connectionFilter)



def test_search_all_collections_paged(DbManager):
    # test case 1: Verify that the function returns a list of documents
    pageSize = 10
    pageNumber = 1
    result = DbManager.search_all_collections_paged(
        pageSize=pageSize,
        pageNumber=pageNumber
    )
    assert isinstance(result, list)

    # test case 2: Verify that the pageSize parameter is working correctly
    pageSize = 20
    result1 = DbManager.search_all_collections_paged(pageSize=pageSize)
    assert len(result1) <= pageSize

    # test case 3: Verify that the pageNumber parameter is working correctly
    pageNumber = 2
    result2 = DbManager.search_all_collections_paged(pageNumber=pageNumber)
    assert result1 != result2 # assume page 2 is different

    # test case 4: Verify that the function handles optional parameters correctly
    startTime = "2021-06-09T13:11:08"
    endTime = "2021-09-09T13:11:08"
    longStart = -22
    longEnd = 10
    latStart = 50
    latEnd = 81
    country = "NorthZone"
    type_ = "RadioactiveWeasel"
    include_edges = True
    pageNumber = 1
    result = DbManager.search_all_collections_paged(
        pageSize=pageSize,
        pageNumber=pageNumber,
        startTime=startTime,
        endTime=endTime,
        longStart=longStart,
        longEnd=longEnd,
        latStart=latStart,
        latEnd=latEnd,
        country=country,
        type=type_,
        include_edges=include_edges
    )
    # perform assertions on the result

    # assert that the result is a list
    assert isinstance(result, list)

    # assert that the result is not empty
    assert len(result) > 0

    # assert that each document in the result meets the specified criteria
    for document in result:
        assert document['doc']["timestamp"] >= startTime
        assert document['doc']["timestamp"] <= endTime
        assert document['doc']["longitude"] >= longStart
        assert document['doc']["longitude"] <= longEnd
        assert document['doc']["latitude"] >= latStart
        assert document['doc']["latitude"] <= latEnd
        assert document['doc']["country"] == country
        assert document["doc"]["species"] == type_
    


def test_search_all_collections(DbManager):
    # test case 1: Verify that the function returns a list of documents
    result = DbManager.search_all_collections()
    assert isinstance(result, list)

    # test case 2: Verify that the function handles optional parameters correctly
    startTime = "2021-06-09T13:11:08"
    endTime = "2021-09-09T13:11:08"
    longStart = -22
    longEnd = 10
    latStart = 50
    latEnd = 80
    country = "NorthZone"
    type_ = "RadioactiveWeasel"
    include_edges = True
    result = DbManager.search_all_collections(
        startTime=startTime,
        endTime=endTime,
        longStart=longStart,
        longEnd=longEnd,
        latStart=latStart,
        latEnd=latEnd,
        country=country,
        type=type_,
        include_edges=include_edges
    )
    # perform assertions on the result

    # assert that the result is a list
    assert isinstance(result, list)

    # assert that the result is not empty
    assert len(result) > 0

    # assert that each document in the result meets the specified criteria
    for document in result:
        assert document['doc']["timestamp"] >= startTime
        assert document['doc']["timestamp"] <= endTime
        assert document['doc']["longitude"] >= longStart
        assert document['doc']["longitude"] <= longEnd
        assert document['doc']["latitude"] >= latStart
        assert document['doc']["latitude"] <= latEnd
        assert document['doc']["country"] == country
        assert document["doc"]["species"] == type_
     

    # test case 3: assert no edges
    result = DbManager.search_all_collections(include_edges=False)

    assert "connectedDocs" not in result
