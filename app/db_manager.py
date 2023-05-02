__author__ = "Maxwell Twente"
__copyright__ = ""
__credits__ = ["Maxwell Twente, "]
__license__ = ""
__version__ = ""
__maintainer__ = "Maxwell Twente"
__email__ = "mtwente@colsa.com"
__status__ = "development"

#UNCLASSIFIED
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

                
    def get_all_documents(self, collection_name, limit = 100):
        """Return a list of all documents in the collection
        """
        if self.has_collection(collection_name):
            print(collection_name)
            collection = self.db.collection(collection_name)
            test = []
            for i in collection.all(skip = 0, limit = limit):
                test.append(i)
            return test
        else:
            print("no collection")
            return list()
                                        
    
    def get_recent_documents(self, collection_name, hours_ago):
        """Return a list of recent documents from the collection
        """
        dt_start, dt_end = start_end_times_from_hoursago(hoursago=hours_ago)
        result = list()
        time_col = "start_time"
        if self.has_collection(collection_name):
            collection = self.db.collection(collection_name)
            query = "LET dtprev = DATE_TIMESTAMP(@dt_start)" + \
                    " FOR doc in " + collection_name + \
                    " FILTER DATE_TIMESTAMP(doc.@time_col) >= dtprev" + \
                    " RETURN doc"
            result = self.aql_execute(
                query,
                bind_vars={"dt_start":dt_start, "time_col":time_col}
            )
        return result
    

    def get_specified_documents(self, collection_names, startTime="",
                                endTime="", longStart="", longEnd="",
                                latStart="", latEnd="", country="",
                                type="", attribute1Start = "", 
                                attribute1End = "", attribute2Start = "",
                                attribute2End = "", include_edges="", exclude_edges=False):
        """
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
            print("results count: " + len(result))

        return result
    
    def get_specified_documents_pages(self, collection_names, page_size=10, page_number=1, startTime="",
                                endTime="", longStart="", longEnd="",
                                latStart="", latEnd="", country="",
                                type="", attribute1Start = "", 
                                attribute1End = "", attribute2Start = "",
                                attribute2End = "", include_edges="", exclude_edges=False):
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

            # print("Query parameters: \n", query_params)
            print("results count: " + len(result))
    
    def get_intersections(self):
        # Specify the collection names
        collection_names = ['sightings', 'audio', 'video']

        # Create a list of document ids for each collection
        doc_ids_list = []
        for collection_name in collection_names:
            collection = self.db.collection(collection_name)
            doc_ids = [doc['_id'] for doc in collection.find({'_id': {'$exists': True}})]
            doc_ids_list.append(doc_ids)

        # Find the intersection of the document ids
        common_doc_ids = set(doc_ids_list[0]).intersection(*doc_ids_list[1:])

        # Retrieve the documents with the common ids
        common_docs = []
        for doc_id in common_doc_ids:
            for collection_name in collection_names:
                collection = self.db.collection(collection_name)
                document = collection.get(doc_id)
                if document is not None:
                    common_docs.append(document)

        return common_docs

    #maybe this will work?
# This query uses the ANY SHORTEST_PATH traversal to traverse 
# the graph from the starting event_id vertex to all vertices
#  that satisfy the specified conditions. The FILTER statements 
# are used to filter the vertices based on their type, datetime, 
# location, country, and edge connections. The RETURN DISTINCT v 
# statement is used to return only the unique vertices that satisfy 
# the conditions.
# Note: that you will need to replace the placeholder values 
# (event_id, collection_name, etc.) with the actual names and IDs
#  of your ArangoDB collections and vertices. Also, you will need 
# to provide the values for the query parameters
#  (start_date, end_date, polygon, country_name, etc.) at runtime.
def complex_query(self, database_name):

    # # Query all events that have combinations of data source A, B and C
    # query = '''
    #     FOR v1, e1, p1 IN 1..1 OUTBOUND 'event_id' edge_collection_name
    #     FOR v2, e2, p2 IN 1..1 OUTBOUND v1._id edge_collection_name
    #     FOR v3, e3, p3 IN 1..1 OUTBOUND v2._id edge_collection_name
    #     FILTER p1.edges[*].type ALL == "data source A" AND
    #            p2.edges[*].type ALL == "data source B" AND
    #            p3.edges[*].type ALL == "data source C"
    #     RETURN DISTINCT
    #     '''

    # Construct the query
    query = '''
        FOR v, e, p IN ANY SHORTEST_PATH
            'event_id'
            TO
            FILTER v.type IN ['X', 'Y', 'Z']
            AND v.datetime >= start_date
            AND v.datetime <= end_date
            AND GEO_CONTAINS(polygon, [v.lon, v.lat])
            AND v.country == 'country_name'
            AND LENGTH(DOC(collection_name, v._id, "inbound_edges")) == 0
            AND (
                (e.edges[*].type ALL == 'data source A' AND p.vertices[*].type ALL != 'data source A')
                OR (e.edges[*].type ALL == 'data source B' AND p.vertices[*].type ALL != 'data source B')
                OR (e.edges[*].type ALL == 'data source A' AND p.vertices[*].type ALL == 'data source A')
            )
            RETURN DISTINCT v
    '''

    # Execute the query
    result = self.db.aql.execute(query)

    # Return the result
    return result
#UNCLASSIFIED