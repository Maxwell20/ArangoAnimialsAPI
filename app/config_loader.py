__author__ = "Maxwell Twente"
__copyright__ = ""
__credits__ = ["Maxwell Twente, "]
__license__ = ""
__version__ = ""
__maintainer__ = "Maxwell Twente"
__email__ = "mtwente@colsa.com"
__status__ = "development"
#UNCLASSIFIED
#file@config_loader.py
"""
Config loader loads certificates and ports ect from environment variables.
Contains clases for authentification certificates and hosting configurations.
"""
import os

from abc import ABC, abstractmethod
from collections import namedtuple

UvicornConfig = namedtuple(
    "UvicornConfig",
    "reverse_proxy_on host port ssl_certfile ssl_keyfile ssl_cert_reqs ssl_ca_certs log_config_file"
)

class BaseUvicornConfigLoader(ABC):
    """Base class defining the interface for the creds loader
    """
    @abstractmethod
    def build_config(self):
        """Build and return the ArangoCredentials object
        """
        raise NotImplementedError

class UvicornConfigTestLoader(BaseUvicornConfigLoader):
    """Our test instance does not have auth enabled
    """
    def build_config(self):
        """Just build a dummy config object
        """
        return UvicornConfig(
            host = "0.0.0.0",
            port = 8000          
        )
#this should load from the docker env variables
class UvicornConfigEnvironmentVarLoader(BaseUvicornConfigLoader):
    """ Load Arango config from the environment
    """
    def build_config(self):
        """The things we need are stored in env vars
        """
        try:
            reverse_proxy_on = os.environ["reverse_proxy_on"] 
            host = os.environ["UVICORN_HOST"]
            port = os.environ["UVICORN_PORT"]
            ssl_certfile = os.environ["UVICORN_ssl-certfile"]
            ssl_keyfile = os.environ["UVICORN_ssl-keyfile"]
            ssl_cert_reqs = os.environ["UVICORN_ssl-cert-reqs"]
            ssl_ca_certs = os.environ["UVICORN_ssl-ca-certs"]
            log_config_file = os.environ["UVICORN_log-config"]

            return UvicornConfig(
                reverse_proxy_on = reverse_proxy_on,
                host = host,
                port = port,
                ssl_certfile = ssl_certfile,
                ssl_keyfile = ssl_keyfile,
                ssl_cert_reqs = ssl_cert_reqs,
                ssl_ca_certs = ssl_ca_certs,
                log_config_file = log_config_file,
            )
        # Probably want to think about how we want to fail here
        except Exception as e:
            raise e
