const { getSessionReport } = require("../services/reportServices");

exports.getSessionReport = async (req, res) => {
  try {
    const { studentName } = req.params;
    const report = await getSessionReport(studentName);

    if (!report) {
      return res
        .status(404)
        .json({ error: `No report found for ${studentName}` });
    }
    res.json(report);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
