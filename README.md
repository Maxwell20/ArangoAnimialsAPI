# Getting started
## Activate virtual python environment 

    source env/bin/activate

## to run the app from the main project directory : depricated - keeping for reference
    uvicorn app.main:app --reload
## to run the app from the main project directory : use this instead since we initialize objects in main and main starts uvicorn
    python main.py

point your browser to http://127.0.0.1:8000 to verify the app is running
you can navigate to /docs to view the api capabilities this page is generated automatically by FastAPI. This will be useful for development testing.

## to build the docker image run
    docker image build --tag app-image .

then to verify the image is built run

    docker image ls
you should then see your image listed

## to run the container run
    docker container run --publish 80:80 --name app-container app-image

verify the app is running on http://localhost:80
## to update the required dependancies for the docker image
generate a new requirements.txt file 

    pip freeze > requirements.txt
Then rebuild the docker image and run the container again

# Unit Test
to test a file name the file "test_\<file-to-test>.py" replace \<file-to-test> with the file name the unit test-test. 
then run
    pytest
this will automatically run all the unit test.