const axios = require("axios");

exports.start = async (req, res) => {
  try {
    const { student_name } = req.body; // frontend must send this

    if (!student_name) {
      return res.status(400).json({ error: "student_name is required" });
    }

    const r = await axios.post(process.env.PYTHON_SERVER_URL + "/start", {
      student_name,
    });
    // const r = await axios.post("http://localhost:5001/start", {
    //   student_name,
    // });

    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.stop = async (req, res) => {
  try {
    const r = await axios.post(process.env.PYTHON_SERVER_URL + "/stop");
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.setMode = async (req, res) => {
  try {
    const { mode } = req.body;
    if (!mode) {
      return res.status(400).json({ error: "mode is required" });
    }
    const r = await axios.post(process.env.PYTHON_SERVER_URL + "/set_mode", {
      mode,
    });
    res.json(r.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
};

exports.getMode = async (req, res) => {
  try {
    const r = await axios.get(process.env.PYTHON_SERVER_URL + "/get_mode");
    res.json(r.data);
  } catch (error) {
    res.status(500).json({ error: err.message });
  }
};
