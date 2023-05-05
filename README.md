# Getting started
## Activate virtual python environment 

    source env/bin/activate

## to run the app from the main project directory : depricated - keeping for reference
    uvicorn app.main:app --reload
## to run the app from the main project directory : use this instead since we initialize objects in main and main starts uvicorn
### note: the environment variables in the .env file may only work from vscode for development, in deployment they will come from the docker file
    python main.py

point your browser to http://127.0.0.1:8000 to verify the app is running
you can navigate to /docs to view the api capabilities this page is generated automatically by FastAPI. This will be useful for development testing.

## to build the docker image run
    docker image build --tag app-image .

then to verify the image is built run

    docker image ls
you should then see your image listed

## to run and create the container run
    docker container run --publish 80:80 --name app-container app-image
## to run  and create the container and connect to arango on localhost
    docker container run --publish 80:80 --network="host" --name app-container app-image

verify the app is running on http://localhost:80/docs or http://172.17.0.1/docs
## to update the required dependancies for the docker image
generate a new requirements.txt file 

    pip freeze > requirements.txt
Then rebuild the docker image and run the container again

# Unit Test
to test a file name the file "test_\<file-to-test>.py" replace \<file-to-test> with the file name the unit test-test. 
then run
    pytest
this will automatically run all the unit test.


---------------------------------------------
# update for ssl https 

# Test certs set up.
Please refer to ./certs/certinfo.txt for cert auth set up

# Two way to build and run.
# First is to build with docker. I would suggest using docker-compose below     
    docker build -t app-image:latest
    docker run --rm -d -p 443:443/tcp app-image:latest 

# Second docker-compose
# Build the image:
docker-compose build
# Once the image is built, run the container:
docker-compose up -d
# Or do all at once 
docker-compose up --build -d --remove-orphans --no cache

Once complete goto  
https://www.localhostdomain.com/





IMPRTANT NOTE: you must install pytest. pytest isnt included in the virtual environment as it adds alot of packages and not needed on the deployed version. you need to uninstall pytest to build deployed version. 
    pip install pytest
or 
    pip uninstall pytest