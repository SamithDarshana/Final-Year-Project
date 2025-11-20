
from flask import Flask, jsonify, request
from detection import DetectionWorker
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Connect to MongoDB (adjust URI)
client = MongoClient("mongodb://localhost:27017/")
db = client["smart_classroom"]
reports_collection = db["session_reports"]

# Create one global worker instance
worker = DetectionWorker()

# === Default Thresholds and Modes ===
mode_settings = {
    "lecture": {"eye_conf": 0.8, "yawn_conf": 0.75, "emotion_conf": 0.7},
    "quiz": {"eye_conf": 0.9, "yawn_conf": 0.85, "emotion_conf": 0.75},
    "group": {"eye_conf": 0.7, "yawn_conf": 0.65, "emotion_conf": 0.6}
}

current_mode = {
    "mode": "lecture",
    "eye_conf": 0.8,
    "yawn_conf": 0.75,
    "emotion_conf": 0.7
}


@app.route("/start", methods=["POST"])
def start():
    data = request.get_json()
    student_name = data.get("student_name")

    if not student_name:
        return jsonify({"error": "student_name is required"}), 400

    worker.start(student_name)  # pass student number to worker
    return jsonify({"status": "started", "student_name": student_name})


@app.route("/stop", methods=["POST"])
def stop():
    worker.stop()
    report = worker.get_session_report()

    # Convert ObjectId inside report (if present)
    if "_id" in report and isinstance(report["_id"], ObjectId):
        report["_id"] = str(report["_id"])

    return jsonify({"status": "stopped", "report": report})


@app.route("/latest", methods=["GET"])
def latest():
    return jsonify(worker.get_latest())


@app.route("/report", methods=["GET"])
def report():
    return jsonify(worker.get_session_report() or {})

# ========================
# ⚙️ MODE CONTROL ENDPOINTS
# ========================


@app.route("/set_mode", methods=["POST"])
def set_mode():
    """Change current mode dynamically via API"""
    data = request.get_json()
    mode = data.get("mode", "").lower()

    if mode not in mode_settings:
        return jsonify({
            "error": "Invalid mode",
            "valid_modes": list(mode_settings.keys())
        }), 400

    # Update global mode
    current_mode.update({"mode": mode, **mode_settings[mode]})
    worker.update_thresholds(current_mode)

    return jsonify({
        "status": "mode updated",
        "active_mode": mode,
        "thresholds": current_mode
    })


@app.route("/get_mode", methods=["GET"])
def get_mode():
    """Get currently active mode and thresholds"""
    return jsonify({
        "active_mode": current_mode["mode"],
        "thresholds": current_mode
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True, threaded=True)
