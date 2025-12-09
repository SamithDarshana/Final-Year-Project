const { getParticipantList } = require("../utils/sessionHelpers");

// === In-memory sessions ===
const sessions = new Map();
exports.sessions = sessions;

function generateCode() {
  return Math.floor(100000 + Math.random() * 900000).toString();
}

// --- API Controllers ---
exports.startSession = (req, res) => {
  const code = generateCode();
  sessions.set(code, {
    participants: new Map(), // socket.id → name
    cameraStatus: new Map(), // name → { active: true, socketId }
    active: true,
    presenterSocket: null,
  });
  console.log(`✅ Session started with code: ${code}`);
  res.json({ code });
};

exports.endSession = (req, res) => {
  const code = req.params.code;
  const io = req.app.locals.io;

  if (!sessions.has(code))
    return res.status(404).json({ message: "Session not found" });

  io.to(code).emit("session-ended");
  sessions.delete(code);
  console.log(`🚪 Session ended: ${code}`);
  res.json({ message: "Session ended" });
};

// --- Socket.IO Logic ---
exports.initSocket = (io) => {
  io.on("connection", (socket) => {
    console.log("🧩 New connection:", socket.id);

    socket.on("presenter-join", (code) => {
      const session = sessions.get(code);
      if (!session)
        return socket.emit("error", { message: "Invalid session code" });
      socket.join(code);
      socket.emit(
        "participant-list",
        Array.from(session.participants.values())
      );
      console.log(`Presenter joined session ${code}`);
    });

    socket.on("join-session", ({ name, code }) => {
      const session = sessions.get(code);
      if (!session || !session.active)
        return socket.emit("error", { message: "Invalid or inactive session" });

      // Prevent duplicate names (optional)
      for (const [id, n] of session.participants) {
        if (n === name) {
          return socket.emit("error", { message: "Name already taken" });
        }
      }

      session.participants.set(socket.id, name);
      session.cameraStatus.set(name, { active: false, socketId: socket.id });
      socket.join(code);
      // Notify everyone (including presenter)
      io.to(code).emit("participant-list", getParticipantList(session));
      console.log(`${name} joined session ${code}`);
    });

    socket.on("disconnect", () => {
      for (const [code, session] of sessions.entries()) {
        if (session.participants.delete(socket.id)) {
          io.to(code).emit(
            "participant-list",
            Array.from(session.participants.values())
          );
        }
      }
    });
  });
};

exports.presenter = (req, res) => {
  res.send(`<!DOCTYPE html>
<html>
<head>
<title>Presenter</title>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
</head>
<body>
<h2>Presenter Panel</h2>
<button id="start">Start Session</button>
<button id="end" disabled>End Session</button>
<p>Session Code: <span id="code">-</span></p>
<h3>Participants (<span id="count">0</span>):</h3>
<ul id="participants"></ul>
<ul id="participants"></ul>

<script>
const socket = io();
let currentCode = null;

document.getElementById('start').addEventListener('click', async () => {
  console.log('Starting session...');
  const res = await fetch('http://localhost:3000/api/session/startSession', { method: 'POST' });
  const data = await res.json();
  currentCode = data.code;
  document.getElementById('code').textContent = currentCode;
  document.getElementById('end').disabled = false;

  // Presenter joins the same room
  socket.emit('presenter-join', currentCode);
});

document.getElementById('end').addEventListener('click', async () => {
  if (!currentCode) return alert('No active session');
  const res = await fetch('http://localhost:3000/api/session/endSession/' + currentCode, { method: 'POST' });
  const data = await res.json();
  alert(data.message);
  currentCode = null;
  document.getElementById('code').textContent = '-';
  document.getElementById('end').disabled = true;
  document.getElementById('participants').innerHTML = '';
});

socket.on('participant-list', function(list) {
 console.log('Received participant list:', list);
 const html = list
    .map(p => {
      return \`<li>\${p.name} — Camera: \${p.cameraOn ? "On" : "Off"}</li>\`;
    })
    .join('');
  document.getElementById('participants').innerHTML = html;
      document.getElementById('count').textContent = list.length;
});
</script>
</body>
</html>`);
};

exports.participant = (req, res) => {
  res.send(`<!DOCTYPE html>
<html>
<head>
<title>Participant</title>
<script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
</head>
<body>
<h2>Join Session</h2>
<input id="name" placeholder="Your Name">
<input id="code" placeholder="Session Code">
<button id="join">Join</button>

<script>
const socket = io();

document.getElementById('join').onclick = function() {
  const name = document.getElementById('name').value;
  const code = document.getElementById('code').value;
  console.log(name, code);
  if (!name || !code) {
    return alert('Name and code are required');
  }
  socket.emit('join-session', { name, code });
};

socket.on('error', function(msg) {
  alert(msg.message || msg);
});

socket.on('session-ended', function() {
  alert('Session ended by presenter');
});
</script>
</body>
</html>`);
};
