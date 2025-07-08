// Minimal placeholder Node.js app for orchestration testing
const http = require('http');
const PORT = process.env.COMMAND_NODE_PORT || 3001;
console.log('Starting Aurora Command Node...');
http
  .createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Aurora Command Node is running!\n');
  })
  .listen(PORT, () => {
    console.log(`Command Node listening on port ${PORT}`);
  });
process.on('uncaughtException', err => {
  console.error('Uncaught Exception:', err);
});
process.on('unhandledRejection', err => {
  console.error('Unhandled Rejection:', err);
});
