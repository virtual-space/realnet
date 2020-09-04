FROM python:3.7-slim

WORKDIR /app

COPY realnet ./
COPY setup.py ./
COPY LICENSE ./
COPY README.md ./
COPY runner ./
RUN python -m venv venv
RUN . venv/bin/activate
RUN ./venv/bin/pip install wheel
RUN ./venv/bin/python setup.py sdist bdist_wheel
RUN ./venv/bin/pip install dist/*

CMD [ "./runner" ]
