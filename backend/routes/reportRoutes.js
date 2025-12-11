const { getSessionReport } = require("../controllers/reportController");

const express = require("express");
const { protect, authorize } = require("../middleware/authMiddleware");
const router = express.Router();

router.get("/:studentName", protect, authorize("teacher"), getSessionReport);

module.exports = router;
