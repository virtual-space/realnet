FROM python:3.14.0a3-slim

WORKDIR /app

ADD realnet ./realnet
COPY setup.py ./
COPY LICENSE ./
COPY README.md ./
COPY runner ./
RUN python setup.py install

CMD [ "realnet", "server", "start" ]
