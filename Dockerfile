FROM python:3
ARG REQUIREMENTS

COPY $REQUIREMENTS requirements.txt

RUN pip install -r requirements.txt
