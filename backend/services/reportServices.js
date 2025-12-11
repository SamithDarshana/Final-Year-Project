const Report = require("../models/Report");

// Get student report by name
async function getSessionReport(studentName) {
  const reports = await Report.find({ student_name: studentName })
    .sort({ start_time: -1 }) // newest first
    .lean(); // optional: faster, returns plain JS objects

  return reports;
}

module.exports = {
  getSessionReport,
};
