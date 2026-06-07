# Sample Dockerfile for Node.js Command Node
# TODO(#833): pin to verified SHA256 digest
FROM node:20-alpine
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 3001
CMD ["node", "index.js"]
# Healthcheck: ensure Node.js service is up
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --spider -q http://localhost:3001 || exit 1
