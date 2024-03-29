FROM python:3.11-slim

WORKDIR /app

ADD realnet ./realnet
COPY setup.py ./
COPY LICENSE ./
COPY README.md ./
COPY runner ./
RUN python setup.py install

CMD [ "realnet", "server", "start" ]
