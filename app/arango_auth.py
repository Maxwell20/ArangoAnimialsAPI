import os

from abc import ABC, abstractmethod
from collections import namedtuple

ArangoCredentials = namedtuple(
    "ArangoCredentials",
    "host username password database"
)

class BaseArangoCredentialsLoader(ABC):
    """Base class defining the interface for the creds loader
    """
    @abstractmethod
    def build_credentials(self):
        """Build and return the ArangoCredentials object
        """
        raise NotImplementedError

class ArangoCredentialsTestLoader(BaseArangoCredentialsLoader):
    """Our test instance does not have auth enabled
    """
    def build_credentials(self):
        """Just build a dummy credentials object
        """
        return ArangoCredentials(
            host = "http://localhost:1234/",
            username = 'root',
            password = 'adbpwd',
            database = "SightingsDatabase"
        )
#this should load from the docker env variables
class ArangoCredentialsEnvironmentVarLoader(BaseArangoCredentialsLoader):
    """ Load Arango credentials from the environment
    """
    def build_credentials(self):
        """The things we need are stored in env vars
        """
        try:
            host = os.environ["ARANGO_HOST"]
            username = os.environ["ARANGO_USERNAME"]
            password = os.environ["ARANGO_PASSWORD"]
            database = os.environ["ARANGO_DATABASE"]

            return ArangoCredentials(
                host = host,
                username = username,
                password = password,
                database = database
            )
        # Probably want to think about how we want to fail here
        except Exception as e:
            raise e

