FROM python:3.11.0-slim

WORKDIR /api

RUN apt-get update 

COPY . /api/
RUN pip install -r requirements.txt

RUN pip install docker

EXPOSE 3000

ENTRYPOINT [ "python", "./app.py" ] 