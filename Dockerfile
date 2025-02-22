FROM python:3.11-slim

# Install kubectl
RUN apt-get update && apt-get install -y curl && \
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy application files
ADD realnet ./realnet
COPY setup.py ./
COPY LICENSE ./
COPY README.md ./
COPY runner ./
RUN python setup.py install

# Copy Kubernetes deployment files
COPY k8s/base /app/k8s/base
COPY k8s/deploy.sh /app/k8s/deploy.sh
RUN chmod +x /app/k8s/deploy.sh

# Install required Python packages for MQTT support
RUN pip install paho-mqtt

CMD [ "realnet", "server", "start" ]
