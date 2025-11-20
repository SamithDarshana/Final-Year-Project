const {
  getAllUnreadAlerts,
  getUnreadAlertsByStudentName,
  markAllAlertsAsRead,
} = require("../controllers/alertController");

const express = require("express");
const { protect, authorize } = require("../middleware/authMiddleware");
const router = express.Router();

router.get("/unread", protect, authorize("teacher"), getAllUnreadAlerts);
router.get(
  "/unread/:studentName",
  protect,
  authorize("teacher"),
  getUnreadAlertsByStudentName
);
router.put(
  "/mark-all-read",
  protect,
  authorize("teacher"),
  markAllAlertsAsRead
);

module.exports = router;
