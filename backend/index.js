const express = require("express");
const router = express.Router();
const userRoutes = require("./routes/userRoutes");

// Use user routes
router.use("/user", userRoutes);

// Example GET route
router.get("/hello", (req, res) => {
  res.json({ message: "Hello from API" });
});

module.exports = router;
