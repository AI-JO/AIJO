const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static frontend
app.use(express.static(path.join(__dirname, 'public')));

// Load people data once at startup
const peopleFilePath = path.join(__dirname, 'data', 'people.json');
let peopleByNationalId = {};
try {
  const fileContent = fs.readFileSync(peopleFilePath, 'utf8');
  peopleByNationalId = JSON.parse(fileContent);
} catch (error) {
  console.error('Failed to load people.json:', error);
}

// Health check
app.get('/api/health', (req, res) => {
  res.json({ ok: true });
});

// Lookup person by national ID
app.get('/api/people/:nationalId', (req, res) => {
  const nationalId = req.params.nationalId;
  const person = peopleByNationalId[nationalId];
  if (!person) {
    return res.status(404).json({
      message: 'عذرًا، لم يتم العثور على بيانات لهذا الرقم الوطني.'
    });
  }
  res.json({ nationalId, ...person });
});

// Fallback to index.html for root
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Arabic Voice ID server is running on http://localhost:${PORT}`);
}); 