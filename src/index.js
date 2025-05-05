require('dotenv').config();
const express = require('express');
const captivePortal = require('./captivePortal');
const matrixDisplay = require('./matrixDisplay');
const amazonClient = require('./amazonClient');

const app = express();
const PORT = process.env.PORT || 80;

// Example route to test if server is running
app.get('/', (req, res) => {
res.send('Hello from RPi LED Device!');
});

// This could be your actual captive portal route
app.use('/setup', captivePortal);

// Example route to trigger matrix update with Amazon data
app.get('/update-matrix', async (req, res) => {
try {
const data = await amazonClient.getSalesData();
matrixDisplay.showData(data);
res.send('Matrix updated!');
} catch (error) {
console.error(error);
res.status(500).send('Failed to update matrix');
}
});

app.listen(PORT, () => {
console.log(Server listening on port ${PORT});
});