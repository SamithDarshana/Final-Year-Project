const Alert = require("../models/Alert");

// Get all unread alerts
async function getAllUnreadAlerts() {
  return await Alert.find({ status: "unread" });
}

// Get unread alerts by student name
async function getUnreadAlertsByStudentName(studentName) {
  return await Alert.find({ student_name: studentName, status: "unread" });
}

// Mark all alerts as read
async function markAllAlertsAsRead() {
  return await Alert.updateMany({ status: "unread" }, { status: "read" });
}

module.exports = {
  getAllUnreadAlerts,
  getUnreadAlertsByStudentName,
  markAllAlertsAsRead,
};
