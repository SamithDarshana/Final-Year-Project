const axios = require("axios");
const { sessions } = require("./sessionController");
const { getParticipantList } = require("../utils/sessionHelpers");

// exports.start = async (req, res) => {
//   try {
//     const { student_name } = req.body; // frontend must send this

//     if (!student_name) {
//       return res.status(400).json({ error: "student_name is required" });
//     }

//     const r = await axios.post(process.env.PYTHON_SERVER_URL + "/start", {
//       student_name,
//     });
//     // const r = await axios.post("http://localhost:5001/start", {
//     //   student_name,
//     // });

//     res.json(r.data);
//   } catch (err) {
//     res.status(500).json({ error: err.message });
//   }
// };

exports.start = async (req, res) => {
  try {
    const { student_name, code } = req.body; // Now require code!

    if (!student_name || !code) {
      return res
        .status(400)
        .json({ error: "student_name and code are required" });
    }

    const session = sessions.get(code);
    if (!session || !session.active) {
      return res.status(403).json({ error: "Invalid or inactive session" });
    }

    // Check if this student actually joined?
    const participant = Array.from(session.participants.values()).find(
      (n) => n === student_name
    );
    if (!participant) {
      return res.status(403).json({ error: "You are not in this session" });
    }

    // Mark camera as ON
    session.cameraStatus.set(student_name, { active: true, socketId: null });

    // Notify teacher/frontend
    const io = req.app.locals.io;
    io.to(code).emit("participant-list", getParticipantList(session));

    // Forward to Python server
    const r = await axios.post(process.env.PYTHON_SERVER_URL + "/start", {
      student_name,
      //code // optional: send code too if Python needs it
    });

    res.json({ success: true, ...r.data });
  } catch (err) {
    console.error(err);
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
