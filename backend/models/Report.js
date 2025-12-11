const mongoose = require("mongoose");
const reportSchema = new mongoose.Schema(
  {
    student_name: { type: String, required: true },
    start_time: { type: Date, required: true },
    end_time: { type: Date, required: true },
    session_duration_sec: { type: Number, required: true },
    eye_closures: { type: Number, required: true },
    yawns: { type: Number, required: true },
    drowsiness_alerts: { type: Number, required: true },
  },
  { timestamps: true, collection: "session_reports" }
);

module.exports = mongoose.model("Report", reportSchema);
