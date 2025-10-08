const express = require("express");
const router = express.Router();
const userRoutes = require("./routes/userRoutes");
const modelRoutes = require("./routes/modelRoutes");
const sessionRoutes = require("./routes/sessionRoutes");

// Use user routes
router.use("/user", userRoutes);

// Use model routes
router.use("/model", modelRoutes);

// Use session routes
router.use("/session", sessionRoutes);

// Example GET route
router.get("/hello", (req, res) => {
  res.json({ message: "Hello from API" });
});

module.exports = router;
