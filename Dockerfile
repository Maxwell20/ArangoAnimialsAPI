FROM python:3-slim-buster

#arango db environment variables:
#change these to update db connection service account credentials
ENV ARANGO_HOST="http://localhost:1234/"
ENV ARANGO_DATABASE="SightingsDatabase"
ENV ARANGO_USERNAME="root"
ENV ARANGO_PASSWORD="adbpwd"
#change these to update the uvicorn prot and host
ENV UVICORN_HOST="0.0.0.0"
ENV UVICORN_PORT=80

RUN mkdir /code

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
#change this to change the host and port the api will run on - Depricated use main.py
# CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=80"]
CMD ["python", "app/main.py"]

