__author__ = "Maxwell Twente"
__copyright__ = ""
__credits__ = ["Maxwell Twente, "]
__license__ = ""
__version__ = ""
__maintainer__ = "Maxwell Twente"
__email__ = "mtwente@colsa.com"
__status__ = "development"

# file@conftest.py
# file for pytest/unit test config
def pytest_configure(config):
    import os 
    os.environ["ARANGO_HOST"] = "http://localhost:1234/"
    os.environ["ARANGO_DATABASE"] = "SightingsDatabase"
    os.environ["ARANGO_USERNAME"] = "root"
    os.environ["ARANGO_PASSWORD"] = "adbpwd"
    os.environ["UVICORN_HOST"] = "0.0.0.0"
    os.environ["UVICORN_PORT"] = "443"
    os.environ["UVICORN_ssl-certfile"] = "/home/max/prj/colsa/ArangoAnimalsAPI/app/certs/server.cer"
    os.environ["UVICORN_ssl-keyfile"] = "/home/max/prj/colsa/ArangoAnimalsAPI/app/certs/server.key" 
    os.environ["UVICORN_ssl-cert-reqs"] = "2"
    os.environ["UVICORN_ssl-ca-certs"] = "/home/max/prj/colsa/ArangoAnimalsAPI/app/certs/ca.cer"
    os.environ["UVICORN_log-config"] = "/home/max/prj/colsa/ArangoAnimalsAPI/app/config/log_conf_dev.yml"