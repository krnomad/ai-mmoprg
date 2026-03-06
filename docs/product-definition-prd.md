# Spectator-First AI MMO Prototype — Product Definition (PRD)

## 0) Product Summary
Create a **spectator-first autonomous fantasy battler** where AI-driven squads clash in short, readable matches that are fun to watch in under 60 seconds, with enough strategic depth to keep viewers returning.

**Hard prioritization:**
- Build for **watchability first**, player control second.
- Build a **single excellent game loop** (draft → battle → highlights), not a broad feature set.
- Build systems that a **small team + AI coding tools** can ship in 8–12 weeks.

---

## 1) Problem Statement
Most multiplayer prototypes fail at launch because:
1. They are not fun until deep progression exists.
2. They are difficult to read as spectators.
3. They overbuild infrastructure before proving core entertainment.

We need a prototype that is immediately entertaining as a **show**, not just as a game.

---

## 2) Product Vision
Deliver an "AI arena sport":
- Matches are short, dramatic, and legible.
- Every match generates moments worth clipping.
- Spectators can influence light macro choices (votes/predictions), while AI handles micro combat.

If people would watch even without playing, the concept is validated.

---

## 3) Gameplay Pillars (Non-Negotiable)
1. **Readability over realism**
   - Action must be understandable at a glance.
   - Clear silhouettes, color-coded teams, simple VFX language.

2. **Drama every match**
   - Guaranteed spikes: opening clash, mid-fight swing, final clutch window.
   - Built-in comeback mechanics at squad level (not rubber-banding stats invisibly).

3. **AI personality, not AI chaos**
   - Agents express archetypes (aggressive flanker, cautious support, objective anchor).
   - Behavior must look intentional and repeatably debuggable.

4. **Spectator agency with low friction**
   - Viewers can vote on one pre-match modifier and one mid-match event trigger pool.
   - No high-frequency controls that create noise.

5. **Clip-worthy by design**
   - Auto-highlight detector for kills, turnarounds, objective steals, 1vX survivals.
   - Post-match “Top 3 moments” recap is mandatory for MVP.

---

## 4) Target User Segments
### Primary Segment: Competitive Spectators
- Watch game streams/esports, enjoy theorycraft and outcomes.
- Need clear, fast, emotionally legible matches.
- Success signal: they watch consecutive matches and discuss AI decisions.

### Secondary Segment: Lightweight Participatory Viewers
- Want to influence outcomes without mastering controls.
- Engage through predictions, votes, and faction preference.
- Success signal: repeat voting/prediction participation.

### Tertiary Segment: Systems/AI Enthusiasts
- Interested in observing agent behavior, loadouts, and meta shifts.
- Success signal: they compare builds and request telemetry overlays.

**Explicit deprioritization (MVP):** deep avatar progression players, open-world roleplayers, hardcore manual PvP mains.

---

## 5) Core Loop Definition
1. **Pre-match (30–45s)**
   - Show two AI squads with visible archetypes/loadouts.
   - Spectators vote on one match modifier from 3 options.

2. **Battle (90–150s)**
   - Autonomous squad combat on one compact arena map.
   - One central objective activates mid-match to force conflict.

3. **Resolution (20–30s)**
   - Winner + reason (objective control, wipe, time score).
   - Top 3 auto-generated highlights + quick stats.

4. **Next-match hook (10s)**
   - Tease rematch, rival squads, or altered modifier slate.

Target full cycle: **~3 minutes**.

---

## 6) MVP Scope (Must Ship)
### A. Match Experience
- 1 arena map (symmetrical, high readability lanes).
- 2 teams of 4 AI agents.
- 4 agent archetypes: Tank, Striker, Controller, Support.
- 8 total abilities (2 per archetype) with obvious telegraphs.
- Single win condition framework: score from eliminations + objective control.

### B. Spectator-First UX
- Broadcast camera modes:
  - Auto-director (default)
  - Tactical overhead
  - Follow-hero
- On-screen timeline of key events.
- Live odds/probability bar (simple model based on current state).
- Pre-match vote UI (1 modifier pick).

### C. Engagement Layer
- Prediction: “Which team wins?” before match starts.
- Lightweight account-less session identity (cookie/device ID).
- Streak indicator for prediction accuracy.

### D. Highlights & Replay
- Real-time event tagging.
- End-of-match “Top 3 moments” auto-recap.
- Shareable short match summary link (data-driven page, no video export in MVP).

### E. Operations/Tooling
- Deterministic simulation seed support for replay/debug.
- Basic balance config in JSON/YAML (no custom editor).
- Match telemetry logging for key metrics.

---

## 7) Non-Goals for MVP (Will Not Build)
1. Open world / exploration / questing.
2. Manual player-controlled combat.
3. Guilds, chat moderation stack, social graph.
4. Complex economy, crafting, auction house.
5. Full ranked ladder with anti-cheat.
6. Mobile native client.
7. Advanced machine-learned agents (start with behavior trees/utility AI).
8. Cinematic replay studio.
9. UGC map editor.
10. Monetization systems beyond placeholder hooks.

These are intentionally excluded to protect delivery speed and clarity.

---

## 8) Success Metrics
## 8.1 Prototype Success (first playable, internal + limited external)
Time window: first 2–4 weeks of testing.

- **Watchability:**
  - ≥70% of viewers watch a full match cycle (~3 min).
  - Median session ≥2 consecutive matches.
- **Readability:**
  - ≥80% can correctly answer “why team A won” in post-match prompt.
- **Excitement:**
  - ≥40% of matches produce at least 1 tagged highlight rated “exciting” by testers.
- **Stability:**
  - Match completion rate ≥95% (no crashes/desyncs).

## 8.2 MVP Success (public alpha)
Time window: first 30 days after release.

- **Retention/engagement:**
  - D1 viewer return ≥30%
  - D7 viewer return ≥12%
  - Average matches per session ≥3.5
- **Spectator participation:**
  - Vote participation rate ≥50% of live viewers.
  - Prediction participation rate ≥35% of live viewers.
- **Entertainment output:**
  - ≥1.2 highlights per match on average.
  - ≥25% of sessions open at least one recap/share page.
- **Production viability:**
  - Small-team ops: ≤5% matches require manual intervention.
  - Balance cadence: one meaningful tuning update/week possible without code deploy.

---

## 9) Build Constraints & Team Shape
Assume team of **4–6**:
- 1 gameplay engineer
- 1 full-stack engineer
- 1 technical designer
- 1 UI/UX + motion generalist
- (optional) 1 data/infra hybrid

AI coding assistance usage:
- Autogenerate boilerplate (UI scaffolding, telemetry schemas, test fixtures).
- Assist with bot behavior iteration and deterministic test coverage.
- Human-reviewed balancing and spectator UX decisions only.

Technical simplifications:
- Single region deployment for MVP.
- Authoritative server sim, thin web client.
- No microservices unless proven necessary.

---

## 10) Prioritized Delivery Plan (Hard Cuts)
### Phase 1: “Is it fun to watch?”
- Core combat sandbox
- Auto-director camera
- Event timeline
- Internal highlight tagging

### Phase 2: “Can viewers influence and return?”
- Pre-match vote
- Winner prediction
- Recap page

### Phase 3: “Can we operate it cheaply?”
- Telemetry dashboards
- Balance config pipeline
- Replay determinism checks

If schedule slips, cut in this order:
1. Follow-hero camera
2. Live odds bar
3. Shareable recap page styling polish

Never cut: readability, highlight recap, match stability.

---

## 11) Risks & Mitigations
- **Risk:** AI behavior looks random/confusing.
  - **Mitigation:** constrain archetypes + behavior debug overlays + deterministic seeds.

- **Risk:** Matches feel repetitive with one map.
  - **Mitigation:** rotating modifiers and objective spawn patterns before adding new maps.

- **Risk:** Spectator tools clutter screen.
  - **Mitigation:** default minimalist HUD + progressive disclosure overlays.

- **Risk:** Overengineering backend early.
  - **Mitigation:** monolith-first architecture; weekly complexity review with deletion bias.

---

## 12) One-Sentence MVP Definition
A web-viewable, 3-minute autonomous squad battle experience where spectators can vote/predict outcomes, enjoy clear AI-driven action, and receive an auto-generated highlight recap worth sharing.
