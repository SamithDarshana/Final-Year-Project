const express = require("express");
const cors = require("cors");
const path = require("path");
const http = require("http");
const { Server } = require("socket.io");
require("dotenv").config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

const connectDB = require("./config/db");

// Connect to MongoDB
connectDB();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname))); // serve HTML files

// Load routes from index.js
app.use("/api", require("./index"));

// Default route
app.get("/", (req, res) => {
  res.send("Backend is running 🚀");
});

// Start server
const PORT = process.env.PORT || 5000;
server.listen(PORT, () =>
  console.log(`Server + Socket.IO running on port ${PORT}`)
);

// model routes
// app.post("/start", async (req, res) => {
//   try {
//     const { student_name } = req.body; // frontend must send this

//     if (!student_name) {
//       return res.status(400).json({ error: "student_number is required" });
//     }

//     const r = await axios.post("http://localhost:5000/start", {
//       student_name,
//     });

//     res.json(r.data);
//   } catch (err) {
//     res.status(500).json({ error: err.message });
//   }
// });

// app.get("/latest", async (req, res) => {
//   try {
//     const r = await axios.get("http://localhost:5000/latest");
//     res.json(r.data);
//   } catch (err) {
//     res.status(500).json({ error: err.message });
//   }
// });

// app.post("/stop", async (req, res) => {
//   try {
//     const r = await axios.post("http://localhost:5000/stop");
//     res.json(r.data);
//   } catch (err) {
//     res.status(500).json({ error: err.message });
//   }
// });

// app.get("/report", async (req, res) => {
//   try {
//     const r = await axios.get("http://localhost:5000/report");
//     res.json(r.data);
//   } catch (err) {
//     res.status(500).json({ error: err.message });
//   }
// });
