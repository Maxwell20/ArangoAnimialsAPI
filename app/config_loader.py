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

"""Example Google style docstrings.

This module demonstrates documentation as specified by the `Google Python
Style Guide`_. Docstrings may extend over multiple lines. Sections are created
with a section header and a colon followed by a block of indented text.

Example:
    Examples can be given using either the ``Example`` or ``Examples``
    sections. Sections support any reStructuredText formatting, including
    literal blocks::

        $ python example_google.py

Section breaks are created by resuming unindented text. Section breaks
are also implicitly created anytime a new section starts.

Attributes:
    module_level_variable1 (int): Module level variables may be documented in
        either the ``Attributes`` section of the module docstring, or in an
        inline docstring immediately following the variable.

        Either form is acceptable, but the two should not be mixed. Choose
        one convention to document module level variables and be consistent
        with it.

Todo:
    * For module TODOs
    * You have to also use ``sphinx.ext.todo`` extension

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""
import os

from abc import ABC, abstractmethod
from collections import namedtuple

UvicornConfig = namedtuple(
    "UvicornConfig",
    "host port ssl_certfile ssl_keyfile ssl_cert_reqs ssl_ca_certs log_config"
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
            host = os.environ["UVICORN_HOST"]
            port = os.environ["UVICORN_PORT"]
            ssl_certfile = os.environ["UVICORN_ssl-certfile"]
            ssl_keyfile = os.environ["UVICORN_ssl-keyfile"]
            ssl_cert_reqs = os.environ["UVICORN_ssl-cert-reqs"]
            ssl_ca_certs = os.environ["UVICORN_ssl-ca-certs"]
            log_config = os.environ["UVICORN_log-config"]

            return UvicornConfig(
                host = host,
                port = port,
                ssl_certfile = ssl_certfile,
                ssl_keyfile = ssl_keyfile,
                ssl_cert_reqs = ssl_cert_reqs,
                ssl_ca_certs = ssl_ca_certs,
                log_config = log_config,
            )
        # Probably want to think about how we want to fail here
        except Exception as e:
            raise e
