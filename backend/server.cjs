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

// Attach io to app locals (so controllers can access it)
app.locals.io = io;

const { initSocket } = require("./controllers/sessionController");
initSocket(io);

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

module.exports = app;

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

// // === Socket.IO logic ===
// io.on("connection", (socket) => {
//   console.log("🧩 New connection:", socket.id);

//   // Presenter joins room
//   socket.on("presenter-join", (code) => {
//     const session = sessions.get(code);
//     if (!session)
//       return socket.emit("error", { message: "Invalid session code" });
//     socket.join(code);
//     socket.emit("participant-list", Array.from(session.participants.values()));
//     console.log(`Presenter joined session ${code}`);
//   });

//   // Participant joins
//   socket.on("join-session", ({ name, code }) => {
//     const session = sessions.get(code);
//     if (!session || !session.active)
//       return socket.emit("error", { message: "Invalid or inactive session" });

//     session.participants.set(socket.id, name);
//     socket.join(code);
//     io.to(code).emit(
//       "participant-list",
//       Array.from(session.participants.values())
//     );
//     console.log(`${name} joined session ${code}`);
//   });

//   // Handle disconnect
//   socket.on("disconnect", () => {
//     for (const [code, session] of sessions.entries()) {
//       if (session.participants.delete(socket.id)) {
//         io.to(code).emit(
//           "participant-list",
//           Array.from(session.participants.values())
//         );
//       }
//     }
//   });
// });

// exports.presenter = (req, res) => {
//   res.send(`<!DOCTYPE html>
// <html>
// <head>
// <title>Presenter</title>
// <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
// </head>
// <body>
// <h2>Presenter Panel</h2>
// <button id="start">Start Session</button>
// <button id="end" disabled>End Session</button>
// <p>Session Code: <span id="code">-</span></p>
// <h3>Participants (<span id="count">0</span>):</h3>
// <ul id="participants"></ul>
// <ul id="participants"></ul>

// <script>
// const socket = io();
// let currentCode = null;

// document.getElementById('start').addEventListener('click', async () => {
//   console.log('Starting session...');
//   const res = await fetch('http://localhost:3000/api/session/startSession', { method: 'POST' });
//   const data = await res.json();
//   currentCode = data.code;
//   document.getElementById('code').textContent = currentCode;
//   document.getElementById('end').disabled = false;

//   // Presenter joins the same room
//   socket.emit('presenter-join', currentCode);
// });

// document.getElementById('end').addEventListener('click', async () => {
//   if (!currentCode) return alert('No active session');
//   const res = await fetch('/end-session/' + currentCode, { method: 'POST' });
//   const data = await res.json();
//   alert(data.message);
//   currentCode = null;
//   document.getElementById('code').textContent = '-';
//   document.getElementById('end').disabled = true;
//   document.getElementById('participants').innerHTML = '';
// });

// socket.on('participant-list', function(list) {
//  console.log('Received participant list:', list);
//   const html = list.map(n => '<li>' + n + '</li>').join('');
//   document.getElementById('participants').innerHTML =
//         list.map(name => '<li>' + name + '</li>').join('');
//       document.getElementById('count').textContent = list.length;
// });
// </script>
// </body>
// </html>`);
// };

// exports.participant = (req, res) => {
//   res.send(`<!DOCTYPE html>
// <html>
// <head>
// <title>Participant</title>
// <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
// </head>
// <body>
// <h2>Join Session</h2>
// <input id="name" placeholder="Your Name">
// <input id="code" placeholder="Session Code">
// <button id="join">Join</button>

// <script>
// const socket = io();

// document.getElementById('join').onclick = function() {
//   const name = document.getElementById('name').value;
//   const code = document.getElementById('code').value;
//   console.log(name, code);
//   if (!name || !code) {
//     return alert('Name and code are required');
//   }
//   socket.emit('join-session', { name, code });
// };

// socket.on('error', function(msg) {
//   alert(msg.message || msg);
// });

// socket.on('session-ended', function() {
//   alert('Session ended by presenter');
// });
// </script>
// </body>
// </html>`);
// };
