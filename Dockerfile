FROM python:3.7-slim

WORKDIR /app

COPY realnet ./
COPY setup.py ./
COPY runner ./

CMD [ "./runner" ]
