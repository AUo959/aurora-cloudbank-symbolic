// Minimal placeholder Node.js app for orchestration testing
const http = require('http');
const PORT = 3001;
http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Aurora Command Node is running!\n');
}).listen(PORT, () => {
  console.log(`Command Node listening on port ${PORT}`);
});
