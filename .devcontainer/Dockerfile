# Base image with Node.js 20
FROM mcr.microsoft.com/devcontainers/javascript-node:20

# Install Python 3 and pip for the backend
RUN apt-get update \
    && apt-get install -y python3 python3-pip \
    && apt-get clean

# Ensure node and npm are in the PATH for all shells and users
RUN ln -sf $(which node) /usr/local/bin/node \
    && ln -sf $(which npm) /usr/local/bin/npm \
    && echo 'export PATH=/usr/local/bin:$PATH' > /etc/profile.d/node.sh

USER node
WORKDIR /workspace
