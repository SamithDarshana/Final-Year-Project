const express = require("express");
const axios = require("axios");
const router = express.Router();
const userRoutes = require("./routes/userRoutes");
const modelRoutes = require("./routes/modelRoutes");
const sessionRoutes = require("./routes/sessionRoutes");
const alertRoutes = require("./routes/alertRoutes");

// Use user routes
router.use("/user", userRoutes);

// Use model routes
router.use("/model", modelRoutes);

// Use session routes
router.use("/session", sessionRoutes);

// Use alert routes
router.use("/alert", alertRoutes);

// Example GET route
router.get("/hello", (req, res) => {
  res.json({ message: "Hello from API" });
});

// Face login and screen sharing routes
router.post("/model/face-login", async (req, res) => {
  try {
    const response = await axios.post(
      "http://127.0.0.1:5001/start-face-login"
    );
    res.json(response.data);
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ error: "Face login failed" });
  }
});

// Screen sharing route in student dashboard
router.post("/model/start", async (req, res) => {
  try {
    const response = await axios.post(
      "http://127.0.0.1:5002/start"
    );
    res.json(response.data);
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ error: "Screen sharing failed" });
  }
});


module.exports = router;
