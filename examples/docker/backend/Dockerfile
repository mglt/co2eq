FROM python:3.8-slim-buster

WORKDIR /app

## for development 
## requirements.txt co2eq-0.0.3* are only here before the package is published
## The up-to-date package is generated as follows in the main co2eq directory.
## python3 -m build && pip3 install --force-reinstall  dist/co2eq-0.0.3.tar.gz && cp dist/co2eq-0.0.3* examples/docker/
## Similarly the newest version of the countryinfo package shoudl be installed 

## a) building dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
## b) install co2eq from local source
COPY co2eq-0.0.3.tar.gz co2eq-0.0.3.tar.gz
COPY conf_rep_cities.json conf_rep_cities.json
## c) install the co2eq package
RUN pip3 install --force-reinstall co2eq-0.0.3.tar.gz


## installation of the co2eq package
#RUN pip3 install co2eq

EXPOSE 8000

COPY . .

CMD [ "python3", "server.py"]
#CMD [ "python3", "../../src/co2eq/meeting_list_server.py"]
#CMD [ "python3", "meeting_list_server.py"]
