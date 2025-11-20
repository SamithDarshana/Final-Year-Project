const mongoose = require("mongoose");

const alertSchema = new mongoose.Schema(
  {
    student_name: { type: String, required: true },
    event_type: { type: String, required: true, default: "drowsiness_alert" },
    status: { type: String, enum: ["read", "unread"], required: true },
  },
  { timestamps: true }
);

module.exports = mongoose.model("Alert", alertSchema);
