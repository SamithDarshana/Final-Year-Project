const express = require("express");
const cors = require("cors");
require("dotenv").config();
const connectDB = require("./config/db");
const axios = require("axios");

// Connect to MongoDB
connectDB();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Load routes from index.js
app.use("/api", require("./index"));

// Default route
app.get("/", (req, res) => {
  res.send("Backend is running 🚀");
});

// model routes
app.post("/start", async (req, res) => {
  try {
    const r = await axios.post("http://localhost:5000/start");
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/latest", async (req, res) => {
  try {
    const r = await axios.get("http://localhost:5000/latest");
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/stop", async (req, res) => {
  try {
    const r = await axios.post("http://localhost:5000/stop");
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/report", async (req, res) => {
  try {
    const r = await axios.get("http://localhost:5000/report");
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
// Start server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
