const express = require("express");
const { register, login, getUsers } = require("../controllers/userController");
const { protect, authorize } = require("../middleware/authMiddleware");
const router = express.Router();

// public routes
router.post("/register", register);
router.post("/login", login);

// protected routes
router.get("/", protect, authorize("teacher"), getUsers);

module.exports = router;
