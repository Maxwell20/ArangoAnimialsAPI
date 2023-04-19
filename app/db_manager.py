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
    
    # def get_specified_documents(self, collection_name, bound = "", startTime= "", endTime= "", longStart = None, longEnd = None, latStart = None, latEnd = None, country = "", type = ""):
    #     result = list()
    #     # Define the query parameters
    #     query_params = {
    #         "start_time": startTime,
    #         "end_time": endTime,
    #         "latStart": latStart,
    #         "latEnd": latEnd,
    #         "longStart": longStart,
    #         "longEnd": longEnd,
    #         "country": country,
    #         "species": type
    #     }
        
    #     if self.has_collection(collection_name):
    #         # Define the name of the collection to query
    #         collection = self.db.collection(collection_name)
    #         # Build the AQL query string
    #         aql_query = """
    #                     FOR doc IN @@collection
    #                     FILTER (!@start_time || doc.timestamp >= @start_time OR doc.latitude == null)
    #                     FILTER (!@end_time || doc.timestamp <= @end_time OR doc.latitude == null)
    #                     FILTER (!@latitude || doc.latitude >= @latStart OR doc.latitude == null)
    #                     FILTER (!@latitude || doc.latitude <= @latEnd OR doc.latitude == null)
    #                     FILTER (!@longitude || doc.longitude >= @longStart OR doc.longitude == null)
    #                     FILTER (!@longitude || doc.longitude <= @longEnd OR doc.longitude == null)                     
    #                     FILTER (!@country || doc.country == @country OR doc.country == null)
    #                     FILTER (!@species || doc.species == @species OR doc.species == null)
    #                     RETURN doc
    #                     """
    #         # Prepare the query for execution
    #         result = self.aql_execute(
    #             aql_query,
    #                 bind_vars={
    #                     "@collection": collection_name,
    #                     **query_params
    #                  }
    #         )

    #         print("Populated query: \n", aql_query.format(
    #         start_time_filter="(!@start_time || doc.timestamp >= DATE_TIMESTAMP(@start_time))",
    #         end_time_filter="(!@end_time || doc.timestamp <= DATE_TIMESTAMP(@end_time))",
    #         latitude_filter="(!@latitude || doc.latitude == @latitude)",
    #         longitude_filter="(!@longitude || doc.longitude == @longitude)"
    #             ))
    #         print("Query parameters: \n", query_params)
    #         print(result)

    #     return result
    
# def get_specified_documents(self, collection_name, bound="", startTime="", endTime="", longStart=None, longEnd=None, latStart=None, latEnd=None, country=None, type=None):
#     result = list()
#     # Define the query parameters
#     query_params = {
#         "start_time": startTime,
#         "end_time": endTime,
#         "latStart": latStart,
#         "latEnd": latEnd,
#         "longStart": longStart,
#         "longEnd": longEnd,
#         "country": country,
#         "species": type
#     }
    
#     if self.has_collection(collection_name):
#         # Define the name of the collection to query
#         collection = self.db.collection(collection_name)
#         # Build the AQL query string
#         aql_query = """
#                     FOR doc IN @@collection
#                     FILTER (!@start_time || doc.timestamp >= @start_time OR doc.latitude == null)
#                     FILTER (!@end_time || doc.timestamp <= @end_time OR doc.latitude == null)
#                     FILTER (!@latStart || !@latEnd || (doc.latitude >= @latStart AND doc.latitude <= @latEnd) OR doc.latitude == null)
#                     FILTER (!@longStart || !@longEnd || (doc.longitude >= @longStart AND doc.longitude <= @longEnd) OR doc.longitude == null)                     
#                     FILTER (!@country || doc.country == @country OR doc.country == null)
#                     FILTER (!@species || doc.species == @species OR doc.species == null)
#                     RETURN doc
#                     """
#         # Prepare the query for execution
#         result = self.aql_execute(
#             aql_query,
#                 bind_vars={
#                     "@collection": collection_name,
#                     **query_params
#                  }
#         )

#         print("Populated query: \n", aql_query.format(
#         start_time_filter="(!@start_time || doc.timestamp >= DATE_TIMESTAMP(@start_time))",
#         end_time_filter="(!@end_time || doc.timestamp <= DATE_TIMESTAMP(@end_time))"
#             ))
#         print("Query parameters: \n", query_params)
#         print(result)

#     return result
    
# def get_specified_documents(self, collection_names, bound="", startTime="", endTime="", longStart=None, longEnd=None, latStart=None, latEnd=None, country="", type=""):
#     result = list()

#     # Define the query parameters
#     query_params = {
#         "start_time": startTime,
#         "end_time": endTime,
#         "latStart": latStart,
#         "latEnd": latEnd,
#         "longStart": longStart,
#         "longEnd": longEnd,
#         "country": country,
#         "species": type
#     }

#     # Create an empty list to hold the results from each collection
#     all_results = []

#     # Loop over each collection name in the list
#     for collection_name in collection_names:
#         if self.has_collection(collection_name):
#             # Define the name of the collection to query
#             collection = self.db.collection(collection_name)

#             # Build the AQL query string
#             aql_query = """
#                         FOR doc IN @@collection
#                         FILTER (!@start_time || doc.timestamp >= @start_time OR doc.latitude == null)
#                         FILTER (!@end_time || doc.timestamp <= @end_time OR doc.latitude == null)
#                         FILTER (!@latitude || doc.latitude >= @latStart OR doc.latitude == null)
#                         FILTER (!@latitude || doc.latitude <= @latEnd OR doc.latitude == null)
#                         FILTER (!@longitude || doc.longitude >= @longStart OR doc.longitude == null)
#                         FILTER (!@longitude || doc.longitude <= @longEnd OR doc.longitude == null)                     
#                         FILTER (!@country || doc.country == @country OR doc.country == null)
#                         FILTER (!@species || doc.species == @species OR doc.species == null)
#                         RETURN doc
#                         """

#             # Prepare the query for execution
#             results = self.aql_execute(
#                 aql_query,
#                 bind_vars={
#                     "@collection": collection_name,
#                     **query_params
#                 }
#             )

#             # Add the results to the list of all results
#             all_results.extend(results)

#             print("Populated query: \n", aql_query.format(
#                 start_time_filter="(!@start_time || doc.timestamp >= DATE_TIMESTAMP(@start_time))",
#                 end_time_filter="(!@end_time || doc.timestamp <= DATE_TIMESTAMP(@end_time))",
#                 latitude_filter="(!@latitude || doc.latitude == @latitude)",
#                 longitude_filter="(!@longitude || doc.longitude == @longitude)"
#             ))
#             print("Query parameters: \n", query_params)
#             print(results)

#     # Combine the results from all collections into a single list
#     result = all_results

#     return result

# It can handle:

# Find all sightings that occurred in December of 2019
# Find all sightings that occurred between 01/01/1970 and 01/01/1999
# Find all sightings that occurred in the Equatorial Zone
# Find all sightings that occurred in the Equatorial Zone and are species Eagle
# Find all RadioactiveWeasels regardless of time, country, place
# Find all RadioactiveWeasels that also have satellite and trail cam video collections
# Within a polygon (lat/lon) Ex: (lat=-10 to 10, lon=0,60)
# That have trail cam audio files associated

# However, it cannot handle the following cases:

# Find all sightings of RadioactiveWeasels that have telescope and satellite data collections associated
# Find all RadioactiveWeasels that have satellite data and attribute 1 <= 0.5
# Find all files associated with a specific sighting
# Find all files associated with a specific trail cam audio file (other audio files, sightings, anything linked to the sighting)
# For a specific satellite collect, find all other collects that are within 10 seconds and 5 km, assuming the radius of the planet is the same as the earth. Do not use sighting node (search other indices)
# Each of these cases requires additional query parameters and filtering conditions.

# For the case "Of RadioactiveWeasels (regardless of time, country, place)": You can modify the query to include a filter for the species "RadioactiveWeasels" and remove the other filters (such as time, country, and place).
# For the case "Within a polygon (lat/lon)": You can modify the query to include a filter for the latitude and longitude ranges specified in the polygon.
# For the case "That have trail cam audio files associated": You can modify the query to include a filter for the presence of trail cam audio files in the associated files.
# For the case "That have telescope and satellite data collections associated": You can modify the query to include a filter for the presence of telescope and satellite data collections in the associated files.
# For the case "That have satellite data and attribute 1 <= 0.5": You can modify the query to include a filter for the attribute 1 value being less than or equal to 0.5 in the files that have satellite data.
# For the case "For a specific satellite collect, find all other collects that are within 10 seconds and 5 km, assuming the radius of the planet is the same as the earth. Do not use sighting node (search other indices)": This case requires a more complex operation that involves searching for files based on time and distance from a specific satellite collect. It is not possible to modify the current query to handle this case.
# def get_specified_documents(self, collection_names, bound="", startTime="", endTime="", longStart=None, longEnd=None, latStart=None, latEnd=None, country="", type="", include_edges=False):
#     result = []

#     # Define the query parameters
#     query_params = {
#         "start_time": startTime,
#         "end_time": endTime,
#         "latStart": latStart,
#         "latEnd": latEnd,
#         "longStart": longStart,
#         "longEnd": longEnd,
#         "country": country,
#         "species": type,
#         "include_edges": include_edges
#     }

#     if isinstance(collection_names, str):
#         collection_names = [collection_names]

#     if self.has_collection(collection_names):
#         # Define the names of the collections to query
#         collections = [self.db.collection(collection_name) for collection_name in collection_names]
#         # Build the AQL query string
#         aql_query = """
#                     FOR doc IN @@collections
#                     FILTER (!@start_time || doc.timestamp >= @start_time OR doc.latitude == null)
#                     FILTER (!@end_time || doc.timestamp <= @end_time OR doc.latitude == null)
#                     FILTER (!@latitude || doc.latitude >= @latStart OR doc.latitude == null)
#                     FILTER (!@latitude || doc.latitude <= @latEnd OR doc.latitude == null)
#                     FILTER (!@longitude || doc.longitude >= @longStart OR doc.longitude == null)
#                     FILTER (!@longitude || doc.longitude <= @longEnd OR doc.longitude == null)                     
#                     FILTER (!@country || doc.country == @country OR doc.country == null)
#                     FILTER (!@species || doc.species == @species OR doc.species == null)
#                     LET edges = @include_edges ? (
#                         FOR e IN @@collections[*] FILTER e._from == doc._id || e._to == doc._id RETURN e
#                     ) : []
#                     RETURN {doc, edges}
#                     """
#         # Prepare the query for execution
#         result = self.aql_execute(
#             aql_query,
#             bind_vars={
#                 "@collections": collections,
#                 **query_params
#             }
#         )

#         print("Populated query: \n", aql_query.format(
#             start_time_filter="(!@start_time || doc.timestamp >= DATE_TIMESTAMP(@start_time))",
#             end_time_filter="(!@end_time || doc.timestamp <= DATE_TIMESTAMP(@end_time))",
#             latitude_filter="(!@latitude || doc.latitude == @latitude)",
#             longitude_filter="(!@longitude || doc.longitude == @longitude)"
#         ))
#         print("Query parameters: \n", query_params)
#         print(result)

#     return result

    def get_specified_documents(self, collection_names, startTime="", endTime="", longStart="", longEnd="", latStart="", latEnd="", country="", type="", attribute1 = "", attribute2 = "",  include_edges=""):
        result = []

        # Define the query parameters
        query_params = {
            "start_time": startTime,
            "end_time": endTime,
            "latStart": latStart,
            "latEnd": latEnd,
            "longStart": longStart,
            "longEnd": longEnd,
            "country": country,
            "species": type,
            "attribute1": attribute1,
            "attribute2": attribute2,
            "include_edges": include_edges
        }
        # collections = collection_names
        if isinstance(collection_names, str):
            collection_names = [collection_names]
        for collection in collection_names:
            if self.has_collection(collection):
                # Define the names of the collections to query
                # collections = [self.db.collection(collection_name) for collection_name in collection_names]
                # Build the AQL query string
                #time must be YYYY-MM-DDTHH:mm:ss.sssZ?
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
                                FILTER (!@attribute1 || doc.attribute1 >= @attribute1)
                                FILTER (!@attribute1 || doc.attribute1 <= @attribute1)
                                FILTER (!@attribute2|| doc.attribute2 >= @attribute2)
                                FILTER (!@attribute2 || doc.attribute2 <= @attribute2)
                                LET edges = @include_edges ? (
                                FOR e IN @@collection FILTER e._from == doc._id || e._to == doc._id RETURN e) : []
                                RETURN {doc, edges}
                            """
                # Prepare the query for execution
                result += self.aql_execute(
                    aql_query,
                    bind_vars={
                        "@collection": collection,
                        **query_params
                    }
                )

            # print("Populated query: \n", aql_query.format(
            #     start_time_filter="(!@start_time || doc.timestamp >= DATE_TIMESTAMP(@start_time))",
            #     end_time_filter="(!@end_time || doc.timestamp <= DATE_TIMESTAMP(@end_time))",
            #     latitude_filter="(!@latitude || doc.latitude == @latitude)",
            #     longitude_filter="(!@longitude || doc.longitude == @longitude)"
            # ))
            print("Query parameters: \n", query_params)
            print(result)

        return result


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