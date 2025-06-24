const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Serve the index.ejs with a dynamic API URL
app.get('/', (req, res) => {
  const apiUrl = process.env.VITE_API_URL || 'http://localhost:8001/';
  res.render('index', { apiUrl });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});