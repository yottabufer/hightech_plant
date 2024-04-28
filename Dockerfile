FROM python:3.11.8-alpine3.19

COPY task/req.txt /req.txt
COPY /task /task
WORKDIR /task
EXPOSE 8000
RUN pip install -r /req.txt