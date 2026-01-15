FROM python:3.14.0a1-slim

# Install kubectl
RUN apt-get update && apt-get install -y curl && \
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy setup files first for better layer caching
COPY setup.py ./
COPY LICENSE ./
COPY README.md ./

# Install dependencies
RUN pip install --no-cache-dir -e .

# Copy application files
ADD realnet ./realnet
COPY runner ./

# Copy Kubernetes deployment files
COPY k8s/base /app/k8s/base
COPY k8s/deploy.sh /app/k8s/deploy.sh
RUN chmod +x /app/k8s/deploy.sh

CMD [ "realnet", "server", "start" ]
