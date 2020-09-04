FROM python:3.7-slim

WORKDIR /app

COPY realnet ./
COPY setup.py ./
COPY runner ./
RUN python setup.py install

CMD [ "./runner" ]
