const {
  getAllUnreadAlerts,
  getUnreadAlertsByStudentName,
  markAllAlertsAsRead,
} = require("../services/alertServices");

exports.getAllUnreadAlerts = async (req, res) => {
  try {
    const alerts = await getAllUnreadAlerts();
    if (!alerts) {
      return res.status(404).json({ error: "No unread alerts found" });
    }
    res.json(alerts);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.getUnreadAlertsByStudentName = async (req, res) => {
  try {
    const { studentName } = req.params;
    const alerts = await getUnreadAlertsByStudentName(studentName);
    if (!alerts || alerts.length === 0) {
      return res
        .status(404)
        .json({ error: `No unread alerts found for ${studentName}` });
    }
    res.json(alerts);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.markAllAlertsAsRead = async (req, res) => {
  try {
    const result = await markAllAlertsAsRead();
    res.json({ message: `All alerts marked as read` });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
