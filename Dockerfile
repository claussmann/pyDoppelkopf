FROM python:slim-bookworm
EXPOSE 8000

COPY requirements.txt .
RUN python3 -m ensurepip
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

RUN mkdir /App
COPY doppelkopf_server /App/doppelkopf_server

WORKDIR /App
RUN adduser --system --no-create-home erwin
USER erwin

ENTRYPOINT uvicorn doppelkopf_server.main:app --host 0.0.0.0 --port 8000