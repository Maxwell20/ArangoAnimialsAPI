FROM python:3-slim-buster

#arango db environment variables:
#change these to update db connection service account credentials
ENV ARANGO_HOST="http://exo-arangodb:8529/"
ENV ARANGO_DATABASE="SightingsDatabase"
ENV ARANGO_USERNAME="root"
ENV ARANGO_PASSWORD="adbpwd"
#change these to update the uvicorn prot and host
ENV UVICORN_HOST="0.0.0.0"
ENV UVICORN_PORT="8080"
ENV reverse_proxy_on="true"
ENV UVICORN_ssl-certfile="/code/certs/rest_server.cer"
ENV UVICORN_ssl-keyfile="/code/certs/rest_server.key" 
ENV UVICORN_ssl-cert-reqs="2" 
ENV UVICORN_ssl-ca-certs="/code/certs/ca.cer"
ENV UVICORN_log-config="/code/config/log_conf.yml"

RUN mkdir /code
RUN mkdir /run_log

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .
#change this to change the host and port the api will run on - Depricated use main.py
# CMD ["uvicorn", "app.main:app", "--host=0.0.0.0", "--port=80"]
CMD ["python", "app/main.py"]

EXPOSE 8080