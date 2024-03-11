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

app.get('/getclcodes', (req, res)=>{

  var path = 'http://127.0.0.1:5000/getclcodes';
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
server.listen(3000, () => {
  console.log('Server listening on port 3000');
});
