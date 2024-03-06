const express = require('express');
// const https = require('https');
const http = require('http');
const fs = require('fs');

const app = express();

// Replace with your actual certificate and key paths
// const cert = fs.readFileSync('path/to/your/server.crt');
// const key = fs.readFileSync('path/to/your/server.key');

// const options = {
//   cert,
//   key
// };

const server = http.createServer(app);

// Express route handler (replace with your desired logic)
app.get('/getpages', (req, res) => {
  res.send('<h1>This are get Pages</h1>');
});

app.get('/getrecommendation', (req, res) => {
  res.send('<h1>This is get recommendation</h1>');
});
server.listen(3000, () => {
  console.log('Server listening on port 3000');
});
