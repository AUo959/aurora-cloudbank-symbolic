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
FROM mcr.microsoft.com/devcontainers/javascript-node:20  # TODO(#833): pin to verified SHA256 digest for supply-chain integrity

# Install Python 3 and pip for the backend
RUN apt-get update \
    && apt-get install -y python3 python3-pip \
    && apt-get clean

# Ensure bash is the default shell and configure for Copilot Chat compatibility
RUN chsh -s /bin/bash node

# Set up clean bash environment for Copilot Chat visibility
RUN echo '# Aurora CloudBank - Clean Bash Profile for Copilot Chat' > /home/node/.bashrc \
    && echo 'export PS1="\u@\h:\w\$ "' >> /home/node/.bashrc \
    && echo 'export GPG_TTY=$(tty)' >> /home/node/.bashrc \
    && echo 'export PYTHONUNBUFFERED=1' >> /home/node/.bashrc \
    && echo 'export NODE_OPTIONS="--no-warnings"' >> /home/node/.bashrc \
    && echo 'stty -ixon 2>/dev/null || true' >> /home/node/.bashrc

# --- DO NOT add extra PATH or symlink steps, Node/npm already correct ---

USER node
WORKDIR /workspace
