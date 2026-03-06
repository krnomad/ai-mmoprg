const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const connectBtn = document.getElementById("connectBtn");
const spectatorBtn = document.getElementById("spectatorBtn");
const statusText = document.getElementById("status");
const serverUrlInput = document.getElementById("serverUrl");
const chatLog = document.getElementById("chatLog");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");

const TILE_SIZE = 32;
const DEFAULT_MAP = { width: 30, height: 17 };

const state = {
  ws: null,
  connected: false,
  spectator: false,
  playerId: null,
  map: { ...DEFAULT_MAP },
  entities: new Map(),
  speechBubbles: [],
};

function setStatus(message) {
  statusText.textContent = message;
}

function addChatLine(text) {
  const line = document.createElement("li");
  line.textContent = text;
  chatLog.appendChild(line);
  while (chatLog.children.length > 70) {
    chatLog.removeChild(chatLog.firstChild);
  }
  chatLog.scrollTop = chatLog.scrollHeight;
}

function send(payload) {
  if (!state.ws || state.ws.readyState !== WebSocket.OPEN) {
    return;
  }
  state.ws.send(JSON.stringify(payload));
}

function connect() {
  if (state.ws) {
    state.ws.close();
    state.ws = null;
  }

  const url = serverUrlInput.value.trim();
  const ws = new WebSocket(url);
  state.ws = ws;
  setStatus(`Connecting: ${url}`);

  ws.addEventListener("open", () => {
    state.connected = true;
    setStatus(`Connected: ${url}`);
    send({ type: "hello", spectator: state.spectator });
  });

  ws.addEventListener("close", () => {
    state.connected = false;
    setStatus("Disconnected");
  });

  ws.addEventListener("error", () => {
    setStatus("Connection error");
  });

  ws.addEventListener("message", (event) => {
    try {
      const message = JSON.parse(event.data);
      handleMessage(message);
    } catch {
      addChatLine(`[system] ${event.data}`);
    }
  });
}

function setEntity(entityPatch) {
  const existing = state.entities.get(entityPatch.id) || {
    hp: 100,
    maxHp: 100,
    x: 0,
    y: 0,
    type: "npc",
    name: entityPatch.id,
  };

  state.entities.set(entityPatch.id, {
    ...existing,
    ...entityPatch,
  });
}

function handleMessage(message) {
  switch (message.type) {
    case "welcome":
      state.playerId = message.playerId || state.playerId;
      if (message.map) state.map = message.map;
      if (Array.isArray(message.entities)) {
        message.entities.forEach(setEntity);
      }
      addChatLine(`[system] joined as ${state.playerId ?? "unknown"}`);
      break;
    case "snapshot":
      if (message.map) state.map = message.map;
      if (Array.isArray(message.entities)) {
        state.entities.clear();
        message.entities.forEach(setEntity);
      }
      break;
    case "entity":
      if (message.remove) {
        state.entities.delete(message.id);
      } else {
        setEntity(message);
      }
      break;
    case "chat": {
      const sender = message.name || message.from || "unknown";
      addChatLine(`${sender}: ${message.text || ""}`);
      break;
    }
    case "speech":
      state.speechBubbles.push({
        id: message.id,
        text: message.text,
        expiresAt: performance.now() + 2400,
      });
      break;
    default:
      break;
  }
}

function drawMap() {
  const cols = state.map.width || DEFAULT_MAP.width;
  const rows = state.map.height || DEFAULT_MAP.height;
  const width = cols * TILE_SIZE;
  const height = rows * TILE_SIZE;
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }

  for (let y = 0; y < rows; y += 1) {
    for (let x = 0; x < cols; x += 1) {
      const even = (x + y) % 2 === 0;
      ctx.fillStyle = even ? "#2c3e50" : "#263646";
      ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
    }
  }
}

function colorFor(entity) {
  if (entity.id === state.playerId) return "#6de08d";
  if (entity.type === "monster") return "#e05c5c";
  if (entity.type === "npc") return "#d2c268";
  return "#72b7ff";
}

function drawEntity(entity) {
  const px = entity.x * TILE_SIZE + TILE_SIZE / 2;
  const py = entity.y * TILE_SIZE + TILE_SIZE / 2;

  ctx.fillStyle = colorFor(entity);
  ctx.beginPath();
  ctx.arc(px, py, TILE_SIZE * 0.3, 0, Math.PI * 2);
  ctx.fill();

  const hpRatio = Math.max(0, Math.min(1, (entity.hp ?? 0) / (entity.maxHp || 100)));
  const barWidth = TILE_SIZE * 0.8;
  const barX = px - barWidth / 2;
  const barY = py - TILE_SIZE * 0.7;

  ctx.fillStyle = "#00000099";
  ctx.fillRect(barX, barY, barWidth, 5);
  ctx.fillStyle = "#41d96f";
  ctx.fillRect(barX, barY, barWidth * hpRatio, 5);

  ctx.fillStyle = "#f4f7ff";
  ctx.font = "12px sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(`${entity.name} (${Math.round(entity.hp ?? 0)} HP)`, px, barY - 6);
}

function drawSpeechBubbles(now) {
  state.speechBubbles = state.speechBubbles.filter((bubble) => bubble.expiresAt > now);

  for (const bubble of state.speechBubbles) {
    const entity = state.entities.get(bubble.id);
    if (!entity) continue;
    const px = entity.x * TILE_SIZE + TILE_SIZE / 2;
    const py = entity.y * TILE_SIZE - TILE_SIZE * 0.9;

    const text = bubble.text.slice(0, 28);
    ctx.font = "11px sans-serif";
    const width = ctx.measureText(text).width + 14;
    const height = 22;

    ctx.fillStyle = "#101522dd";
    ctx.fillRect(px - width / 2, py - height, width, height);
    ctx.fillStyle = "#f1f5ff";
    ctx.textAlign = "center";
    ctx.fillText(text, px, py - 7);
  }
}

function render(now) {
  drawMap();
  for (const entity of state.entities.values()) {
    drawEntity(entity);
  }
  drawSpeechBubbles(now);

  requestAnimationFrame(render);
}

function attemptMove(dx, dy) {
  if (state.spectator || !state.playerId) return;
  const player = state.entities.get(state.playerId);
  if (!player) return;

  const nextX = Math.max(0, Math.min((state.map.width || DEFAULT_MAP.width) - 1, player.x + dx));
  const nextY = Math.max(0, Math.min((state.map.height || DEFAULT_MAP.height) - 1, player.y + dy));

  player.x = nextX;
  player.y = nextY;
  send({ type: "move", id: state.playerId, x: nextX, y: nextY });
}

window.addEventListener("keydown", (event) => {
  const keyToDelta = {
    ArrowUp: [0, -1],
    ArrowDown: [0, 1],
    ArrowLeft: [-1, 0],
    ArrowRight: [1, 0],
    w: [0, -1],
    a: [-1, 0],
    s: [0, 1],
    d: [1, 0],
  };

  const delta = keyToDelta[event.key];
  if (!delta) return;

  event.preventDefault();
  attemptMove(delta[0], delta[1]);
});

connectBtn.addEventListener("click", connect);

spectatorBtn.addEventListener("click", () => {
  state.spectator = !state.spectator;
  spectatorBtn.textContent = `Spectator: ${state.spectator ? "On" : "Off"}`;
  spectatorBtn.setAttribute("aria-pressed", String(state.spectator));
  send({ type: "spectator", enabled: state.spectator });
});

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = chatInput.value.trim();
  if (!text) return;
  send({ type: "chat", text });
  send({ type: "speech", text });
  chatInput.value = "";
});

// Usable fallback state when no server is present.
setEntity({ id: "player-local", name: "You", x: 4, y: 4, type: "player", hp: 100, maxHp: 100 });
setEntity({ id: "npc-shop", name: "Merchant", x: 7, y: 5, type: "npc", hp: 80, maxHp: 80 });
setEntity({ id: "mob-1", name: "Slime", x: 10, y: 8, type: "monster", hp: 35, maxHp: 50 });
state.playerId = "player-local";
addChatLine("[system] Client ready. Connect to a server to sync live state.");
requestAnimationFrame(render);
