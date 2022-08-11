FROM ubuntu:20.04

RUN apt-get update && apt-get install -y python3-pip
RUN apt -y install unixodbc-dev

COPY . /app/service
RUN pip3 install -r requirements.txt

CMD python3 ./app.py