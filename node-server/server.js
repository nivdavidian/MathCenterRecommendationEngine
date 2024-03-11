const express = require('express');
// const https = require('https');
const http = require('http');
const fs = require('fs');
const axios = require('axios');
const cors = require('cors');

const app = express();

// Replace with your actual certificate and key paths
// const cert = fs.readFileSync('path/to/your/server.crt');
// const key = fs.readFileSync('path/to/your/server.key');

// const options = {
//   cert,
//   key
// };

const server = http.createServer(app);

app.use(cors());

app.get('/getpages', (req, res) => {

  var path = req.query.term ? 
    `http://127.0.0.1:5000/getpages?term=${encodeURIComponent(req.query.term)}` : 
    'http://127.0.0.1:5000/getpages';

  
  // Use template literals correctly with backticks (`) and ${} for variables
  axios.get(path, {
    headers: {
      'Content-Type': 'application/json' // Not typically needed for GET requests
    }
  }) // Ensure you're using backticks (`), not single quotes (')
  .then(response => {
    // Instead of logging, send the data back to the client

    res.send(response.data); // Send the data obtained from the other server to the user
  })
  .catch(error => {
    console.error(error);
    // It's a good practice to handle errors and send an error response
    res.status(500).send('An error occurred while fetching data from the server.');
  });
});

app.get('/getrecommendation', (req, res) => {
  const workksheet_uid = encodeURIComponent(req.query.worksheet_uid); // If the URL is "/getpages?term=something", term will be "something"
  
  // Use template literals correctly with backticks (`) and ${} for variables
  axios.get(`http://127.0.0.1:5000/getrecommendation?worksheet_uid=${workksheet_uid}`, {
    headers: {
      'Content-Type': 'application/json' // Not typically needed for GET requests
    }
  }) // Ensure you're using backticks (`), not single quotes (')
  .then(response => {
    
    res.send(response.data); // Send the data obtained from the other server to the user
  })
  .catch(error => {
    console.error(error);
    // It's a good practice to handle errors and send an error response
    res.status(500).send('An error occurred while fetching data from the server.');
  });
});
server.listen(3000, () => {
  console.log('Server listening on port 3000');
});
