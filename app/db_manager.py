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
file@db_manager.py
Base classes and functionality for database management.
"""
from arango import ArangoClient
from datetime_utils import *
from datetime import datetime
import logging

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

        self.db = self.client.db(
            self.database_name,
            username = self.username,
            password = self.password            
        )

    def get_collection_names(self):
        collections = []
        edgeCollections = []
        for c in self.db.collections():
            print(c)
            if c['system'] != True:   
                if c['type'] == "document":
                    collections.append(c['name'])
                if c['type'] == "edge":
                    edgeCollections.append(c['name'])
            
        return collections, edgeCollections

    def create_collection(self, collectionName, collection_schema, edge=False):
        """Create a collection with schema validation provided by
           the dictionary
        """
        if not self.has_collection(collectionName):
            collection = self.db.create_collection(collectionName, edge=edge)
            collection.configure(schema=collection_schema)
            return collection
        else:
            return self.db.collection(collectionName)


    def has_collection(self, collectionName):
        """ Ask if the database has the given collection
        """
        return self.db.has_collection(collectionName)


    def aql_execute(self, query_string, bind_vars={}):
        """Apply the query using AQL and return the results
           as a list
        """
        log = logging.getLogger(__name__)
        log.debug('QSTRING_______ %s' , query_string)
        log.debug('BIND_VARS_______ %s' , bind_vars)
        return [
            document for document in self.db.aql.execute(
                query_string, bind_vars=bind_vars
            )
        ]


    def add_batch_to_collection(self, collectionName, batch):
        """Use import bulk to add a batch to the collection
           provided. If the collection does not exist,
           create it with no schema.
        """
        is_edge_batch = ("_from" in batch[0] and "_to" in batch[0])
        if self.has_collection(collectionName):
            collection = self.db.collection(collectionName)
        else:
            collection = self.create_collection(
                collectionName,
                collection_schema={},
                edge=is_edge_batch
            ) 

        if is_edge_batch:
            # check whether each _from, _to pair already exists in
            # the collection. Add if does not exist.

            for element in batch:
                fromStr = element["_from"]
                toStr = element["_to"]
                query = "FOR doc in " + collectionName + \
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


    def filter_connected_docs(self, aqlResult, collections):
        """
        Function: filter_connected_docs
        Purpose: removes unwanted data from the connections results since we can't do that in the AQL query
        Return only the connected documents from the specified collections
        """

        for item in aqlResult:
            connected_docs = item.get("connectedDocs")
            edges = item.get("edges")

            if connected_docs is not None:
                item["connectedDocs"] = [
                    doc for doc in connected_docs if doc is None or doc["_id"].split('/')[0] in collections
                ]

            if edges is not None:
                item["edges"] = [
                    doc for doc in edges if doc is None or doc["_from"].split('/')[0] in collections or doc["_to"].split('/')[0] in collections
                ]

        return aqlResult
                                                
    def get_document_by_key(self, key, includeEdges):
        """Function: get_document_by_key
           Purpose:Retrieve an item by key
            Args:
                key: The datbase key of the item to retrieve.
            Returns:
                dict: documents, connected_documents
            """
        result = []
        connectedDocs = []

        collections = self.get_collection_names()
        collection_names = collections[0]
        edge_collections = collections[1]
        for collection in collection_names:
            if self.has_collection(collection):
                # build the AQL query string
                # time must be YYYY-MM-DDTHH:mm:ss.sssZ
                aql_query = """
                            FOR doc IN @@collection
                                FILTER doc._key == @key   
                                RETURN doc
                            """
                # prepare the query for execution
                result += self.aql_execute(
                    aql_query,
                    bind_vars={
                        "@collection": collection,
                        "key": key
                    }
                )

                if includeEdges and len(result) > 0:
                    for collection in edge_collections:
                        aql_query = """ 
                                    LET edges = (
                                    FOR e IN @@collection
                                    FILTER e._from == @doc_id || e._to == @doc_id
                                    RETURN e
                                    ) 

                                    LET connectedDocs = (
                                    FOR e IN edges
                                    LET startDoc = DOCUMENT(e._from)
                                    LET endDoc = DOCUMENT(e._to)
                                    RETURN startDoc._id == @doc_id ? endDoc : startDoc
                                    )

                                    RETURN connectedDocs
                                    """
                        res = self.aql_execute(
                        aql_query,
                        bind_vars={
                            "@collection": collection,
                            "doc_id":result[0]['_id']
                            }
                        )
                        if res[0]:
                            connectedDocs += res
                    # break out after all of the edge collections have been searched
                    break 
                    
        # prepare the final result in the desired format
        formatted_result = []
        for doc in result:
            result_item = {
                "doc": doc,
                "edges": [],
                "connectedDocs": []
            }
            formatted_result.append(result_item)
            for connectedDoc in connectedDocs:
                formatted_result[0]["connectedDocs"].append(connectedDoc)
        return formatted_result
        # return result, connectedDocs
    
    def get_document_by_id(self, id, includeEdges):
        """Function: get_document_by_id
           Purpose: Retrieve an item by ID.
        Args:
            id: The ID of the item to retrieve.
        Returns:
            dict: documents, connected_documents
        """
        result = []
        connectedDocs = []

        collections = self.get_collection_names()
        collection_names = collections[0]
        edge_collections = collections[1]
        for collection in collection_names:
            if self.has_collection(collection):
                # build the AQL query string
                # time must be YYYY-MM-DDTHH:mm:ss.sssZ
                aql_query = """
                            FOR doc IN @@collection
                                FILTER doc._id == @id   
                                RETURN doc
                            """
                # prepare the query for execution
                result += self.aql_execute(
                    aql_query,
                    bind_vars={
                        "@collection": collection,
                        "id": id
                    }
                )

                if includeEdges and len(result) > 0:
                    for collection in edge_collections:
                        aql_query = """ 
                                    LET edges = (
                                    FOR e IN @@collection
                                    FILTER e._from == @doc_id || e._to == @doc_id
                                    RETURN e
                                    ) 

                                    LET connectedDocs = (
                                    FOR e IN edges
                                    LET startDoc = DOCUMENT(e._from)
                                    LET endDoc = DOCUMENT(e._to)
                                    RETURN startDoc._id == @doc_id ? endDoc : startDoc
                                    )

                                    RETURN connectedDocs
                                    """
                        res = self.aql_execute(
                        aql_query,
                        bind_vars={
                            "@collection": collection,
                            "doc_id":result[0]['_id']
                            }
                        )
                        if res[0]:
                            connectedDocs += res
                    # break out after all of the edge collections have been searched
                    break 
                    
                      
        # prepare the final result in the desired format
        formatted_result = []
        for doc in result:
            result_item = {
                "doc": doc,
                "edges": [],
                "connectedDocs": []
            }
            formatted_result.append(result_item)
            for connectedDoc in connectedDocs:
                formatted_result[0]["connectedDocs"].append(connectedDoc)
        return formatted_result
    
        return formatted_result


    def get_recent_documents(self, hoursAgo):
        """
        Retrieves recent documents.
        Args:
            int: hours_ago 
        Returns:
            dict: documents
        """
        dt_start, dt_end = start_end_times_from_hoursago(hoursago=hoursAgo)
        result = []
        collection_names = self.get_collection_names()[0]
        for collection_name in collection_names:
            query = """
                    FOR doc IN @@collection
                        FILTER doc.timestamp >= @dt_start
                        RETURN doc
                    """
            result += self.aql_execute(
                query,
                bind_vars={"@collection": collection_name, "dt_start": dt_start}
            )
        return result
    
    def get_specified_documents(self, collections, startTime="",
                                endTime="", longStart="", longEnd="",
                                latStart="", latEnd="", country="",
                                type="", attribute1Start = "", 
                                attribute1End = "", attribute2Start = "",
                                attribute2End = "", edgeCollections = "", excludeEdges=False, connectionFilter= None):
        """Function: get_specified_documents
           Purpose: Retrieves filterd search of specified collections, documents.
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
        if len(edgeCollections) > 0 and edgeCollections[0] != '':
            include_edges = True
        else:
            include_edges = False

        result = []

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
                }

        # define the query parameters

        if isinstance(collections, str):
            collections = [collections]
        if isinstance(edgeCollections, str):
            edgeCollections = [edgeCollections]
        if len(collections) < len(edgeCollections):
            for i in collection:
                edgeCollections.append('')
        for collection, edgeCollection in zip(collections, edgeCollections):         
                # build the AQL query string
                # time must be YYYY-MM-DDTHH:mm:ss.sssZ
                # exclude documents with edges if exclude_edges is True
                # index of collections and corresponding edge collections must match
                if excludeEdges:
                    # get doucuments that do not have edge connections
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
                                """
                    if include_edges:  
                        aql_query += """
                                        LET edges = (
                                        FOR e IN @@edge_collection FILTER e._from == doc._id || e._to == doc._id RETURN e)
                                        LET connectedDocs = (
                                        FOR e IN edges
                                        LET startDoc = DOCUMENT(e._from)
                                        LET endDoc = DOCUMENT(e._to)
                                        RETURN startDoc._id == doc._id ? endDoc : startDoc
                                        ) 
                                        RETURN {doc, edges, connectedDocs}
                                    """
                        # prepare the query for execution
                        result += self.aql_execute(
                        aql_query,
                        bind_vars={
                            "@collection": collection,
                            "@edge_collection": edgeCollection,
                            **query_params
                            }
                        )
                        if connectionFilter:
                            if connectionFilter[0] != '':
                                result = self.filter_connected_docs(result, connectionFilter)
                    else:
                        aql_query += """ RETURN doc """

                        # prepare the query for execution
                        result += self.aql_execute(
                            aql_query,
                            bind_vars={
                                "@collection": collection,
                                **query_params
                            }
                        )

        return result
    
    def sort_documents(self, documents, num_documents):
        """
            Sorts documents in time order and returns most recent
        """
        if documents:
            if 'doc' in documents[0]:
                sorted_documents = sorted(documents, key=lambda x: datetime.fromisoformat(x['doc']['timestamp']), reverse=True)
            else:
                sorted_documents = sorted(documents, key=lambda x: datetime.fromisoformat(x['timestamp']), reverse=True)
            return sorted_documents[:num_documents]
        else:
            return []
    
    def get_specified_documents_pages(self, collections, pageSize=10, pageNumber=1, startTime="",
                                endTime="", longStart="", longEnd="",
                                latStart="", latEnd="", country="",
                                type="", attribute1Start = "", 
                                attribute1End = "", attribute2Start = "",
                                attribute2End = "", edgeCollections = "", excludeEdges=False, connectionFilter= None):
        """Function: get_specified_documents_pages
           Purpose: Retrieves filterd search of specified collections, documents.
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
        if len(edgeCollections) > 0 and edgeCollections[0] != '':
            include_edges = True
        else:
            include_edges = False

        result = []

        # calculate offset
        offset = (pageNumber - 1) * pageSize
        count = pageSize

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
            "offset": offset,
            "count": count
        }


        if isinstance(collections, str):
            collections = [collections]
        if isinstance(edgeCollections, str):
            edgeCollections = [edgeCollections]
        if len(collections) < len(edgeCollections):
            for i in collection:
                edgeCollections.append('')
        for collection, edgeCollection in zip(collections, edgeCollections):
            if self.has_collection(collection):
                # build the AQL query string
                # time must be YYYY-MM-DDTHH:mm:ss.sssZ
                # exclude documents with edges if exclude_edges is True
                # index of collections and corresponding edge collections must match
                if excludeEdges:
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
                                    """
                    if include_edges:  
                        aql_query += """
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
                            "@edge_collection": edgeCollection,
                            "include_edges": str(include_edges),
                            **query_params
                            }
                        )
                        # filters out unwanted connections
                        if connectionFilter:
                            if connectionFilter[0] != '':
                                result = self.filter_connected_docs(result, connectionFilter)
                    else:
                        aql_query += """ RETURN doc """

                        # prepare the query for execution
                        result += self.aql_execute(
                            aql_query,
                            bind_vars={
                                "@collection": collection,
                                **query_params
                            }
                        )
        # remove extra results to fit page size
        result = self.sort_documents(result, pageSize)
        return result
    
    def search_all_collections_paged(self, pageSize=10, pageNumber=1, startTime="",
                                    endTime="", longStart="", longEnd="",
                                    latStart="", latEnd="", country="",
                                    type="", attribute1Start = "", 
                                    attribute1End = "", attribute2Start = "",
                                    attribute2End = "", include_edges=""):
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
        specified_documents = []
        connected_documents = []
        bind_vars = {}
        db_collections = self.get_collection_names()
        collections = db_collections[0]
        edge_collections = db_collections[1]  
        for collection_name in collections:
            # Initialize the AQL query string
            query = f"FOR doc IN {collection_name} "

            # Build the filter conditions based on the provided criteria
            filters = []
            if startTime:
                filters.append(f"doc.timestamp >= '{startTime}'")
            if endTime:
                filters.append(f"doc.timestamp <= '{endTime}'")
            if longStart:
                filters.append(f"doc.longitude >= {longStart}")
            if longEnd:
                filters.append(f"doc.longitude <= {longEnd}")
            if latStart:
                filters.append(f"doc.latitude >= {latStart}")
            if latEnd:
                filters.append(f"doc.latitude <= {latEnd}")
            if country:
                filters.append(f"doc.country == '{country}'")
            if type:
                filters.append(f"doc.species == '{type}'")
            if attribute1Start:
                filters.append(f"doc.attribute1 >= {attribute1Start}")
            if attribute1End:
                filters.append(f"doc.attribute1 <= {attribute1End}")
            if attribute2Start:
                filters.append(f"doc.attribute2 >= {attribute2Start}")
            if attribute2End:
                filters.append(f"doc.attribute2 <= {attribute2End}")

            # Combine the filter conditions into a single AQL filter string
            if filters:
                query += "FILTER " + " && ".join(filters) + " "

            # Calculate the skip value based on the page number and page size
            skip = (pageNumber - 1) * pageSize

            # Append the LIMIT and OFFSET clauses to the AQL query
            query += f"LIMIT {skip}, {pageSize} RETURN doc"


            # Execute the AQL query to get the specified documents
            documents = self.db.aql.execute(query)
            specified_documents.extend(documents)

            if include_edges:
                # Loop through the specified documents and get the connected documents from edge collections
                for doc in documents:
                    # Query the edge collections based on the specified document's _id
                    for edge_collection in edge_collections:
                        edge_query = f"FOR edge IN {edge_collection} FILTER edge._from == @documentId RETURN edge._to"
                        edge_bind_vars = {"documentId": doc["_id"]}
                        connected_docs = self.db.aql.execute(edge_query, bind_vars=edge_bind_vars)
                        connected_documents.extend(connected_docs)
    # prepare the final result in the desired format
        result = []
        for doc in specified_documents:
            result_item = {
                "doc": doc,
                "edges": [],
                "connectedDocs": []
            }
            result.append(result_item)

        if include_edges:
            for edge in connected_documents:
                for item in result:
                    if edge["_from"].split("/")[1] == item["doc"]["_key"]:
                        item["edges"].append(edge)
                        item["connectedDocs"].append(edge["_to"])

        result = self.sort_documents(result, pageSize)

        if include_edges:
            return result
        return result
    
    def search_all_collections(self, startTime="",
                                    endTime="", longStart="", longEnd="",
                                    latStart="", latEnd="", country="",
                                    type="", attribute1Start = "", 
                                    attribute1End = "", attribute2Start = "",
                                    attribute2End = "", include_edges=""):
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
        specified_documents = []
        connected_documents = []
        bind_vars = {}
        db_collections = self.get_collection_names()
        collections = db_collections[0]
        edge_collections = db_collections[1]  
        for collection_name in collections:
            # Initialize the AQL query string
            query = f"FOR doc IN {collection_name} "

            # Build the filter conditions based on the provided criteria
            filters = []
            if startTime:
                filters.append(f"doc.timestamp >= '{startTime}'")
            if endTime:
                filters.append(f"doc.timestamp <= '{endTime}'")
            if longStart:
                filters.append(f"doc.longitude >= {longStart}")
            if longEnd:
                filters.append(f"doc.longitude <= {longEnd}")
            if latStart:
                filters.append(f"doc.latitude >= {latStart}")
            if latEnd:
                filters.append(f"doc.latitude <= {latEnd}")
            if country:
                filters.append(f"doc.country == '{country}'")
            if type:
                filters.append(f"doc.species == '{type}'")
            if attribute1Start:
                filters.append(f"doc.attribute1 >= {attribute1Start}")
            if attribute1End:
                filters.append(f"doc.attribute1 <= {attribute1End}")
            if attribute2Start:
                filters.append(f"doc.attribute2 >= {attribute2Start}")
            if attribute2End:
                filters.append(f"doc.attribute2 <= {attribute2End}")

            # Combine the filter conditions into a single AQL filter string
            if filters:
                query += "FILTER " + " && ".join(filters) + " "

            # Append the LIMIT and OFFSET clauses to the AQL query
            query += "RETURN doc"


            # Execute the AQL query to get the specified documents
            documents = self.db.aql.execute(query)
            specified_documents.extend(documents)

            if include_edges:
                # Loop through the specified documents and get the connected documents from edge collections
                for doc in documents:
                    # Query the edge collections based on the specified document's _id
                    for edge_collection in edge_collections:
                        edge_query = f"FOR edge IN {edge_collection} FILTER edge._from == @documentId RETURN edge._to"
                        edge_bind_vars = {"documentId": doc["_id"]}
                        connected_docs = self.db.aql.execute(edge_query, bind_vars=edge_bind_vars)
                        connected_documents.extend(connected_docs)

    # prepare the final result in the desired format
        result = []
        for doc in specified_documents:
            result_item = {
                "doc": doc,
                "edges": [],
                "connectedDocs": []
            }
            result.append(result_item)

        if include_edges:
            for edge in connected_documents:
                for item in result:
                    if edge["_from"].split("/")[1] == item["doc"]["_key"]:
                        item["edges"].append(edge)
                        item["connectedDocs"].append(edge["_to"])

        if include_edges:
            return result
        
        return specified_documents
#UNCLASSIFIED