""" Base classes and functionality for database management.
    This is similar to what we use but you don't have to use
    it.  
"""
from arango import ArangoClient
from .datetime_utils import start_end_times_from_hoursago


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
            #TODO: change back to database name
            "_system",
            username = self.username,
            password = self.password
        )

        if not self.sys_db.has_database(self.database_name):
            self.sys_db.create_database(self.database_name)

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
    
    def get_specified_documents(self, collection_name, startTime= "", endTime= "", long = None, lat = None, country = "", type = ""):
        result = list()
        # Define the query parameters
        query_params = {
            "start_time": startTime,
            "end_time": endTime,
            "latitude": lat,
            "longitude": long,
            "country": country,
            "species": type
        }
        
        if self.has_collection(collection_name):
            # Define the name of the collection to query
            collection = self.db.collection(collection_name)
            # Build the AQL query string
            aql_query = """
                        FOR doc IN @@collection
                        FILTER (!@start_time || doc.timestamp >= @start_time)
                        FILTER (!@end_time || doc.timestamp <= @end_time)
                        FILTER (!@latitude || doc.latitude == @latitude OR doc.latitude == null)
                        FILTER (!@longitude || doc.longitude == @longitude OR doc.longitude == null)
                        FILTER (!@country || doc.country == @country OR doc.country == null)
                        FILTER (!@species || doc.species == @species OR doc.species == null)
                        RETURN doc
                        """
            # Prepare the query for execution
            result = self.aql_execute(
                aql_query,
                    bind_vars={
                        "@collection": collection_name,
                        **query_params
                     }
            )

            print("Populated query: \n", aql_query.format(
            start_time_filter="(!@start_time || doc.timestamp >= DATE_TIMESTAMP(@start_time))",
            end_time_filter="(!@end_time || doc.timestamp <= DATE_TIMESTAMP(@end_time))",
            latitude_filter="(!@latitude || doc.latitude == @latitude)",
            longitude_filter="(!@longitude || doc.longitude == @longitude)"
                ))
            print("Query parameters: \n", query_params)
            print(result)

        return result
    