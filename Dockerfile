FROM python:3.7-slim

WORKDIR /app

COPY realnet ./
COPY setup.py ./
COPY LICENSE ./
COPY README.md ./
COPY runner ./
RUN python setup.py install

CMD [ "./runner" ]
