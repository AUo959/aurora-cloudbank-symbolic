# Symbolic Anchor: T1 (DevContainer Dockerfile Initialization)
# SRB: Combined Node.js 20 & Python 3 environment for Aurora simulation stack.
# DLP: [devcontainer, python, node, simulation]
# export_manifest: {
#   name: "aurora-cloudbank-devcontainer-image",
#   version: "1.0.0",
#   memory_sealing: "stateless",
#   cli_chain: "001//devcontainer//docker"
# }

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
