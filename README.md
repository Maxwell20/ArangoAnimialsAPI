# Getting started
## Activate virtual python environment 
    source env/bin/activate

## Test certs set up.
Refer to the certificate readme:
    /certs/README_CERTIFICATES.md 
for cert authorization set up.

## Two way to build and run.
## First is to build with docker. use docker-compose:    
    docker build -t app-image:latest
    docker run --rm -d -p 443:443/tcp app-image:latest 

## Second docker-compose
## Build the image:
    docker-compose build
## Once the image is built, run the container:
    docker-compose up -d
## Or do all at once 
    docker-compose up --build -d --remove-orphans --no cache

## to verify the image is built run
    docker image ls
you should then see your image listed

## Once complete go to: 
    https://www.localhostdomain.com/
or
    https://www.localhostdomain.com/docs#
for the swagger docs


# Setup environment variables
## it is recomended to use vscode along with a launch.json file
## located under the <prj>/.vscode/launch.json directory
## you will have to change the paths to your system spec.
## example launch.json for vscode development:
    {
        // Use IntelliSense to learn about possible attributes.
        // Hover to view descriptions of existing attributes.
        // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
        "version": "0.2.0",
        "configurations": [
            {
                "envFile": "/home/max/prj/colsa/ArangoAnimalsAPI/env/pyvenv.cfg",
                "name": "Start",
                "type": "python",
                "request": "launch",
                "program": "app/main.py",
                "console": "integratedTerminal",
                "justMyCode": true,
                "env" : {
                    "ARANGO_HOST": "http://localhost:1234/",
                    "ARANGO_DATABASE": "SightingsDatabase",
                    "ARANGO_USERNAME": "root",
                    "ARANGO_PASSWORD": "adbpwd",
                    "UVICORN_HOST": "0.0.0.0",
                    "UVICORN_PORT": "443",
                    "UVICORN_ssl-certfile":"/home/max/prj/colsa/ArangoAnimalsAPI/app/certs/server.cer",
                    "UVICORN_ssl-keyfile":"/home/max/prj/colsa/ArangoAnimalsAPI/app/certs/server.key" ,
                    "UVICORN_ssl-cert-reqs": "2",
                    "UVICORN_ssl-ca-certs":"/home/max/prj/colsa/ArangoAnimalsAPI/app/certs/ca.cer",
                    "UVICORN_log-config":"/home/max/prj/colsa/ArangoAnimalsAPI/app/config/log_conf_dev.yml"
                },
                "sudo": true
            }
        ]
    }

# Dependancies:
## certificates
this project is intended to run over ssl/tls using https secure protocol.
certificates for testing are located under:
    /certs
refer to the certificate readme file for more information in the certificate folder.


## to update the required dependancies for the docker image
generate a new requirements.txt file 
    pip freeze > requirements.txt
Then rebuild the docker image and run the container again

# Unit Test
to test a file name the file "test_\<file-to-test>.py" replace \<file-to-test> with the file name the unit test-test. 
then run
    pytest
this will automatically run all the unit test.

IMPRTANT NOTE: you must install pytest. pytest isnt included in the virtual environment as it adds alot of packages and not needed on the deployed version. you need to uninstall pytest to build deployed version. 
    pip install pytest
or 
    pip uninstall pytest