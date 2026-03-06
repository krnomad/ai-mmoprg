# Browser Client Design: First Playable Vertical Slice

## Goals and Constraints
- Deliver a playable browser client with clear combat readability and low latency feel.
- Keep the client **thin**: the server is authoritative for simulation, combat, movement validity, and final outcomes.
- Make spectator mode first-class so development, testing, and community viewing share the same rendering path.
- Build robust debug overlays to speed iteration on netcode and gameplay tuning.

---

## 1) Scene Structure

Use a layered scene graph with strict ownership boundaries:

1. **World Root**
   - Tilemap or static background.
   - World-space entities (players, NPCs, projectiles, effects anchors).
   - World-space UI (names, HP bars, speech bubbles, combat text).

2. **Camera Rig**
   - Follow target (player in active mode, selected entity in spectator mode).
   - Smoothing only affects rendering, never authoritative positions.
   - Supports zoom steps (e.g., close/normal/tactical) for readability.

3. **Screen UI Root (HUD)**
   - Ability bar / action prompts.
   - Chat panel.
   - Minimap and party frame placeholders.
   - Status and latency indicators.

4. **Overlay Root**
   - Modal UI (settings, respawn prompt, scoreboard).
   - Debug overlays (network graphs, reconciliation info, hitboxes).

### Entity View Composition
Each world entity is represented by a lightweight `EntityView` composed of:
- `TransformView`: interpolated render position/rotation.
- `Sprite/AnimationView`: current visual state from server state tags.
- `OverheadView`: nameplate, HP, status markers.
- `FeedbackView`: floating combat text anchors, hit flash, cast indicators.

`EntityView` never contains combat or movement rules; it only projects server state.

---

## 2) Rendering Responsibilities

### Client-side responsibilities
- Draw latest confirmed snapshot.
- Interpolate between snapshots for smooth motion.
- Extrapolate briefly for remote actors when packet gaps occur (bounded window).
- Play cosmetic-only effects triggered by server events:
  - damage/heal numbers
  - hit sparks
  - non-authoritative animation blending
- Cull off-screen entities and reduce update cost by distance/importance.

### Server-side (authoritative) responsibilities reflected by client
- Final positions, facing, velocity state, and collision resolution.
- Action acceptance/rejection (cooldowns, range, resources).
- Damage, healing, death, respawn, crowd-control outcomes.
- Visibility and relevance filtering rules (if applicable).

### Snapshot model
- Server sends periodic snapshots + event stream deltas.
- Client keeps short snapshot buffer (e.g., 100–200 ms) and renders at `serverTime - interpolationDelay`.
- Event stream drives one-shot VFX/SFX/combat text with event IDs for dedupe.

---

## 3) UI Layout

Design for immediate playtest readability:

1. **Top-left**
   - Player vitals (HP/resource bars, level/class tag).
   - Optional target frame beneath.

2. **Bottom-center**
   - Primary action bar (3–6 actions for vertical slice).
   - Cooldown radial + key hint labels.

3. **Bottom-left**
   - Chat log and input box.
   - System notifications (join/leave/killfeed-lite).

4. **Top-right**
   - Minimap placeholder and connection stats (ping, packet loss, server tick).

5. **Center/World-space**
   - Nameplates over entities.
   - HP bars above targetable units.
   - Speech bubbles and combat feedback text.

6. **Modal Layer**
   - Settings, controls help, reconnect prompt, spectator roster.

UI should degrade gracefully on smaller resolutions by collapsing optional panels.

---

## 4) State Synchronization With Server

## Network protocol model
- **Client → Server**: input commands only (move intent, ability request, interact, chat).
- **Server → Client**:
  - Snapshot packets (`tick`, `entities[]`, compact state fields).
  - Event packets (`combat`, `speech`, `spawn/despawn`, `state changes`).
  - Acknowledgment metadata (`lastProcessedInputSeq`).

### Client simulation policy
- **Local player movement**: optional prediction for responsiveness.
  - Apply local inputs immediately to a predicted ghost.
  - Reconcile against authoritative snapshots via correction smoothing.
- **Actions/combat**: optimistic UI only, not optimistic outcomes.
  - Show “queued/casting” state instantly.
  - Show damage/hit only upon authoritative event.

### Reconciliation strategy
- Tag each outgoing input with increasing sequence ID.
- Server echoes last processed sequence.
- Client rewinds local predicted state to server truth, reapplies unacknowledged inputs.
- Hard snap if error > threshold; otherwise smooth over short correction window.

### Failure handling
- Snapshot timeout -> connection warning state.
- Extended timeout -> soft disconnect UI + auto-retry.
- Event dedupe by event ID and tick to avoid duplicate combat text/effects.

---

## 5) Input Handling for Human Players

### Input layers
1. **Raw input capture** (keyboard, mouse, optional gamepad).
2. **Action mapping** (rebindable commands: move, basic attack, ability slots, interact, chat, target cycle).
3. **Intent encoding** into minimal command payloads.
4. **Network send queue** with sequence IDs and timestamps.

### Control scheme (initial)
- WASD / click-to-move (choose one primary; support both if feasible).
- Mouse aim/target selection.
- Number keys for abilities.
- Enter for chat focus.
- Tab for target cycle.
- Space for contextual interact/dodge (slice dependent).

### Anti-jank rules
- Ignore gameplay inputs when chat or modal is focused.
- Buffer short action inputs during brief lockouts (e.g., global cooldown startup).
- Rate-limit repeated command packets while preserving responsiveness.

---

## 6) Spectator Mode Behavior

Spectator mode should reuse the same world renderer and UI components with altered control/state rules.

### Entry and roles
- Join as spectator by server-assigned role or post-death fallback.
- Spectators have no controllable avatar authority.

### Camera behavior
- Free camera pan/zoom + optional “follow entity” mode.
- Quick-jump to players via roster list.
- Smooth transitions between followed targets.

### Information policy
- If competitive integrity matters, server filters hidden info per spectator permissions.
- Spectator HUD includes:
  - followed target vitals
  - compact scoreboard/event feed
  - observed latency/tick data

### Interaction limits
- Disable action bar inputs except camera/hud controls.
- Chat permissions configurable by server (read-only, team-only, global).

---

## 7) Display: Speech Bubbles, Names, HP, Combat Feedback

## Nameplates
- Always-on for nearby entities; fade by distance/occlusion rules.
- Color coding by faction/relation (ally/enemy/neutral).
- Include optional icons (party leader, quest target, dead/incapacitated).

### HP bars
- Anchored above entity head with stable screen-space offset.
- Update from authoritative HP values only.
- Smooth visual drain effect allowed, but must converge rapidly to true value.
- Show shield/absorb segment if vertical slice includes mitigation mechanics.

### Speech bubbles
- Trigger from authoritative speech/chat events.
- Bubble stack per entity with max visible count and timeout.
- Cull/merge distant chatter to avoid clutter.
- Accessibility: high-contrast bubble background and scalable font.

### Combat feedback
- Floating numbers (damage/heal/block/crit) from authoritative combat events.
- Color and typography encode event type; avoid revealing hidden data.
- Hit reactions:
  - flash/tint
  - brief shake (small amplitude)
  - impact marker
- Keep lifetime short and pool objects to avoid GC/perf spikes.

---

## 8) Debugging Overlays (Development)

Ship with togglable developer overlays (hotkey + URL/debug flag):

1. **Network overlay**
   - RTT/ping, jitter, packet loss estimate.
   - Snapshot rate, event rate, bytes/sec.
   - Last acked input sequence.

2. **Timing overlay**
   - Client FPS, frame time histogram.
   - Render/update step durations.
   - Main-thread long frame warnings.

3. **Sync overlay**
   - Local player prediction error magnitude.
   - Reconciliation count and hard-snap count.
   - Current interpolation buffer delay.

4. **World diagnostics**
   - Entity count by type, culled vs rendered.
   - Interest/relevance bucket info (if provided by server).
   - Optional collision/hitbox outlines.

5. **Event trace panel**
   - Recent authoritative events (combat/speech/state changes).
   - Deduped IDs and tick ordering visibility.

6. **Input overlay**
   - Current pressed actions and queued commands.
   - Input-to-send latency estimate.

These overlays are client-observed diagnostics only; they do not alter authoritative logic.

---

## 9) Thin-Client Architecture Summary

Recommended browser client modules:
- `net/connection`: transport, packet decode, clock sync.
- `net/stateBuffer`: snapshot/event buffering and interpolation timeline.
- `input/controller`: device input → intent commands.
- `prediction/reconciliation`: local avatar movement prediction only.
- `render/world`: entity views and world-space rendering.
- `render/ui`: HUD, chat, overlays.
- `fx/feedback`: pooled VFX/SFX/combat text driven by server events.
- `debug/overlays`: dev instrumentation UI.

Key rule: the client can **predict presentation**, but the server decides **truth**.
