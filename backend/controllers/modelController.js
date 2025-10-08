const axios = require("axios");

exports.start = async (req, res) => {
  try {
    const { student_name } = req.body; // frontend must send this

    if (!student_name) {
      return res.status(400).json({ error: "student_name is required" });
    }

    const r = await axios.post("http://localhost:5000/start", {
      student_name,
    });

    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.stop = async (req, res) => {
  try {
    const r = await axios.post("http://localhost:5000/stop");
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};
