require('dotenv').config({ path: '/Users/nivdavidian/MathCenterRecommendationEngine/node-server/envParams.env' });

const express = require('express');
const https = require('https');
const fs = require('fs');
const axios = require('axios');
const cors = require('cors');
const path = require('path');
const app = express();

const sslOptions = {
  key: fs.readFileSync(path.resolve(process.env.SSL_KEY_PATH)),
  cert: fs.readFileSync(path.resolve(process.env.SSL_CERT_PATH))
};

// Custom HTTPS agent for Axios
const agent = new https.Agent({
  rejectUnauthorized: false // DO NOT use in production
});

app.use(cors());
app.get('/getclcodes', (req, res)=>{

  var path = 'https://127.0.0.1:8443/getclcodes';
  axios.get(path, {
    'httpsAgent':agent,
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

app.get('/getpages', (req, res) => {
  var term = req.query.term ? req.query.term : '';
  var cCode = req.query.cCode ? req.query.cCode : '';
  var lCode = req.query.lCode ? req.query.lCode : '';

  var path = `http://127.0.0.1:5000/getpages?term=${term}&cCode=${cCode}&lCode=${lCode}`

  
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
  const workksheet_uid = req.query.worksheet_uid ? req.query.worksheet_uid : ''; // If the URL is "/getpages?term=something", term will be "something"
  var cCode = req.query.cCode ? req.query.cCode : '';
  var lCode = req.query.lCode ? req.query.lCode : '';
  
  // Use template literals correctly with backticks (`) and ${} for variables
  axios.get(`http://127.0.0.1:5000/getrecommendation?worksheet_uid=${workksheet_uid}&cCode=${cCode}&lCode=${lCode}`, {
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

// Create HTTPS server
https.createServer(sslOptions, app).listen(443, () => {
  console.log('HTTPS server running on port 443');
});
