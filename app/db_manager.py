__author__ = "Maxwell Twente"
__copyright__ = ""
__credits__ = ["Maxwell Twente, "]
__license__ = ""
__version__ = ""
__maintainer__ = "Maxwell Twente"
__email__ = "mtwente@colsa.com"
__status__ = "development"

#UNCLASSIFIED
#file@db_manager.py
""" Base classes and functionality for database management.
    This is similar to what we use but you don't have to use
    it.  
"""
from arango import ArangoClient
from datetime_utils import *

class ArangoDatabaseManager:
    """Arango database management object
    """
    def __init__(self, host, database_name, username, password):
        self.host = host
        self.database_name = database_name
        self.username = username
        self.password = password

        self._open_connection()


    def _open_connection(self):
        """Initiate a connection with the Arango database server
           and authenticate.
        """
        self.client = ArangoClient(hosts=self.host)
        self.sys_db = self.client.db(
            "_system",
            username = self.username,
            password = self.password
        )

        # if not self.sys_db.has_database(self.database_name):
        #     self.sys_db.create_database(self.database_name)

        self.db = self.client.db(
            self.database_name,
            username = self.username,
            password = self.password            
        )


    def create_collection(self, collection_name, collection_schema, edge=False):
        """Create a collection with schema validation provided by
           the dictionary
        """
        if not self.has_collection(collection_name):
            collection = self.db.create_collection(collection_name, edge=edge)
            collection.configure(schema=collection_schema)
            return collection
        else:
            return self.db.collection(collection_name)


    def has_collection(self, collection_name):
        """ Ask if the database has the given collection
        """
        return self.db.has_collection(collection_name)


    def aql_execute(self, query_string, bind_vars={}):
        """Apply the query using AQL and return the results
           as a list
        """
        return [
            document for document in self.db.aql.execute(
                query_string, bind_vars=bind_vars
            )
        ]


    def add_batch_to_collection(self, collection_name, batch):
        """Use import bulk to add a batch to the collection
           provided. If the collection does not exist,
           create it with no schema.
        """
        is_edge_batch = ("_from" in batch[0] and "_to" in batch[0])
        if self.has_collection(collection_name):
            collection = self.db.collection(collection_name)
        else:
            collection = self.create_collection(
                collection_name,
                collection_schema={},
                edge=is_edge_batch
            ) 

        if is_edge_batch:
            # check whether each _from, _to pair already exists in
            # the collection. Add if does not exist.

            for element in batch:
                fromStr = element["_from"]
                toStr = element["_to"]
                query = "FOR doc in " + collection_name + \
                        " FILTER doc._from == @fromStr \
                        && doc._to == @toStr \
                        RETURN doc._id"
                result = self.aql_execute(
                            query,
                            bind_vars={"fromStr":fromStr, "toStr":toStr}
                         )
                if not result:
                    collection.insert(element, overwrite=True)

        else: # not a batch of edges
            for element in batch:
                collection.insert(element, overwrite=True)

    def filter_connected_docs(self, aql_result, collections):
        """Function: filter_connected_docs
           Purpose: removes unwanted data from the connections results since we cant do
            that in the AQL query
        """
        for item in aql_result:
            connected_docs = item.get("connectedDocs")
            if connected_docs is not None:
                item["connectedDocs"] = [
                    doc for doc in connected_docs if doc is None or doc["_id"].split('/')[0] in collections
                ]
        return aql_result
                                        
    
    def get_recent_documents(self, collections, hours_ago):
        """Return a list of recent documents from the collection
        """
        dt_start, dt_end = start_end_times_from_hoursago(hoursago=hours_ago)
        result = list()
        time_col = "start_time"
        if isinstance(collection_names, str):
            collection_names = [collections]
        for collection_name in collection_names:
            if self.has_collection(collection):
                collection = self.db.collection(collection_name)
                query = "LET dtprev = @dt_start" + \
                        " FOR doc in " + collection_name + \
                        " FILTER doc.@time_col >= dtprev" + \
                        " RETURN doc"
                result += self.aql_execute(
                    query,
                    bind_vars={"dt_start":dt_start, "time_col":time_col}
                )
        return result
    

    def get_specified_documents(self, collection_names, startTime="",
                                endTime="", longStart="", longEnd="",
                                latStart="", latEnd="", country="",
                                type="", attribute1Start = "", 
                                attribute1End = "", attribute2Start = "",
                                attribute2End = "", include_edges="", exclude_edges=False, connection_filter= None):
        """Function: get_specified_documents
           Purpose: returns the filtered result across a list of collections
        """
        result = []

        # define the query parameters
        query_params = {
            "start_time": startTime,
            "end_time": endTime,
            "latStart": latStart,
            "latEnd": latEnd,
            "longStart": longStart,
            "longEnd": longEnd,
            "country": country,
            "species": type,
            "attribute1Start": attribute1Start,
            "attribute1End": attribute1End,
            "attribute2Start": attribute2Start,
            "attribute2End": attribute2End,
            "include_edges": include_edges,
        }
        # collections = collection_names
        if isinstance(collection_names, str):
            collection_names = [collection_names]
        for collection in collection_names:
            if self.has_collection(collection):
                # build the AQL query string
                # time must be YYYY-MM-DDTHH:mm:ss.sssZ
                # exclude documents with edges if exclude_edges is True
                if exclude_edges:
                    aql_query = """
                                FOR doc IN @@collection
                                    FILTER (!@start_time || doc.timestamp >= @start_time)
                                    FILTER (!@end_time || doc.timestamp <= @end_time)
                                    FILTER (!@latStart || doc.latitude >= @latStart)
                                    FILTER (!@latEnd || doc.latitude <= @latEnd)
                                    FILTER (!@longStart || doc.longitude >= @longStart)
                                    FILTER (!@longEnd || doc.longitude <= @longEnd)
                                    FILTER (!@country || doc.country == @country)
                                    FILTER (!@species || doc.species == @species)
                                    FILTER (!@attribute1Start || doc.attribute1 >= @attribute1Start)
                                    FILTER (!@attribute1End || doc.attribute1 <= @attribute1End)
                                    FILTER (!@attribute2Start || doc.attribute2 >= @attribute2Start)
                                    FILTER (!@attribute2End || doc.attribute2 <= @attribute2End)
                                    FILTER LENGTH(FOR e IN @@edge_collection FILTER e._from == doc._id || e._to == doc._id RETURN e) == 0
                                    RETURN doc
                                """
                else:
                    aql_query = """
                                FOR doc IN @@collection
                                    FILTER (!@start_time || doc.timestamp >= @start_time)
                                    FILTER (!@end_time || doc.timestamp <= @end_time)
                                    FILTER (!@latStart || doc.latitude >= @latStart)
                                    FILTER (!@latEnd || doc.latitude <= @latEnd)
                                    FILTER (!@longStart || doc.longitude >= @longStart)
                                    FILTER (!@longEnd || doc.longitude <= @longEnd)
                                    FILTER (!@country || doc.country == @country)
                                    FILTER (!@species || doc.species == @species)
                                    FILTER (!@attribute1Start || doc.attribute1 >= @attribute1Start)
                                    FILTER (!@attribute1End || doc.attribute1 <= @attribute1End)
                                    FILTER (!@attribute2Start || doc.attribute2 >= @attribute2Start)
                                    FILTER (!@attribute2End || doc.attribute2 <= @attribute2End)
                                    LET edges = @include_edges ? (
                                    FOR e IN @@edge_collection FILTER e._from == doc._id || e._to == doc._id RETURN e) : []
                                    LET connectedDocs = @include_edges ? (
                                    FOR e IN edges
                                    LET startDoc = DOCUMENT(e._from)
                                    LET endDoc = DOCUMENT(e._to)
                                    RETURN startDoc._id == doc._id ? endDoc : startDoc
                                    ) : []
                                    RETURN {doc, edges, connectedDocs}
                                """
                # prepare the query for execution
                result += self.aql_execute(
                    aql_query,
                    bind_vars={
                        "@collection": collection,
                        "@edge_collection": "edge-" + collection,
                        **query_params
                    }
                )

            # print("Query parameters: \n", query_params)
            #filters out unwanted connections
            if connection_filter != None:
                result = self.filter_connected_docs(result, connection_filter)
            print("results count: " + len(result))

        return result
    
    def get_specified_documents_pages(self, collection_names, page_size=10, page_number=1, startTime="",
                                endTime="", longStart="", longEnd="",
                                latStart="", latEnd="", country="",
                                type="", attribute1Start = "", 
                                attribute1End = "", attribute2Start = "",
                                attribute2End = "", include_edges="", exclude_edges=False,connection_filter= None):
        """Function: get_specified_documents_pages
           Purpose: returns the filtered result across a list of collections page by page for use with a 
           paged front end
        """
        result = []
        # calculate offset
        offset = (page_number - 1) * page_size
        count = page_size

        # define the query parameters
        query_params = {
            "start_time": startTime,
            "end_time": endTime,
            "latStart": latStart,
            "latEnd": latEnd,
            "longStart": longStart,
            "longEnd": longEnd,
            "country": country,
            "species": type,
            "attribute1Start": attribute1Start,
            "attribute1End": attribute1End,
            "attribute2Start": attribute2Start,
            "attribute2End": attribute2End,
            "include_edges": include_edges,
            "offset": offset,
            "count": count
        }
        # collections = collection_names
        if isinstance(collection_names, str):
            collection_names = [collection_names]
        for collection in collection_names:
            if self.has_collection(collection):
                # build the AQL query string
                # time must be YYYY-MM-DDTHH:mm:ss.sssZ
                # exclude documents with edges if exclude_edges is True
                if exclude_edges:
                    aql_query = """
                                FOR doc IN @@collection
                                    FILTER (!@start_time || doc.timestamp >= @start_time)
                                    FILTER (!@end_time || doc.timestamp <= @end_time)
                                    FILTER (!@latStart || doc.latitude >= @latStart)
                                    FILTER (!@latEnd || doc.latitude <= @latEnd)
                                    FILTER (!@longStart || doc.longitude >= @longStart)
                                    FILTER (!@longEnd || doc.longitude <= @longEnd)
                                    FILTER (!@country || doc.country == @country)
                                    FILTER (!@species || doc.species == @species)
                                    FILTER (!@attribute1Start || doc.attribute1 >= @attribute1Start)
                                    FILTER (!@attribute1End || doc.attribute1 <= @attribute1End)
                                    FILTER (!@attribute2Start || doc.attribute2 >= @attribute2Start)
                                    FILTER (!@attribute2End || doc.attribute2 <= @attribute2End)
                                    FILTER LENGTH(FOR e IN @@edge_collection FILTER e._from == doc._id || e._to == doc._id RETURN e) == 0
                                    SORT doc.timestamp DESC
                                    LIMIT @offset, @count
                                    RETURN doc
                                """            #filters out unwanted connections

                else:
                    aql_query = """
                                FOR doc IN @@collection
                                    FILTER (!@start_time || doc.timestamp >= @start_time)
                                    FILTER (!@end_time || doc.timestamp <= @end_time)
                                    FILTER (!@latStart || doc.latitude >= @latStart)
                                    FILTER (!@latEnd || doc.latitude <= @latEnd)
                                    FILTER (!@longStart || doc.longitude >= @longStart)
                                    FILTER (!@longEnd || doc.longitude <= @longEnd)
                                    FILTER (!@country || doc.country == @country)
                                    FILTER (!@species || doc.species == @species)
                                    FILTER (!@attribute1Start || doc.attribute1 >= @attribute1Start)
                                    FILTER (!@attribute1End || doc.attribute1 <= @attribute1End)
                                    FILTER (!@attribute2Start || doc.attribute2 >= @attribute2Start)
                                    FILTER (!@attribute2End || doc.attribute2 <= @attribute2End)
                                    SORT doc.timestamp DESC
                                    LIMIT @offset, @count
                                    LET edges = @include_edges ? (
                                    FOR e IN @@edge_collection FILTER e._from == doc._id || e._to == doc._id RETURN e) : []
                                    LET connectedDocs = @include_edges ? (
                                    FOR e IN edges
                                    LET startDoc = DOCUMENT(e._from)
                                    LET endDoc = DOCUMENT(e._to)
                                    RETURN startDoc._id == doc._id ? endDoc : startDoc
                                    ) : []
                                    RETURN {doc, edges, connectedDocs}
                                """
                # prepare the query for execution
                result += self.aql_execute(
                    aql_query,
                    bind_vars={
                        "@collection": collection,
                        "@edge_collection": "edge-" + collection,
                        **query_params
                    }
                )
            #filters out unwanted connections
            if connection_filter != None:
                result = self.filter_connected_docs(result, connection_filter)
            # print("Query parameters: \n", query_params)
            print("results count: " + len(result))
            return result
#UNCLASSIFIED