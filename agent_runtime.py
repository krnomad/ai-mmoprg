"""Deterministic first-pass agent runtime integration.

This module introduces a small, testable runtime where player and NPC agents
produce *actions* from perceptions. The runtime itself does not mutate game
state; callers must validate and apply returned actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple


class AgentKind(str, Enum):
    """Different runtime classes of agents."""

    PLAYER = "player"
    NPC = "npc"


class ActionType(str, Enum):
    """Allowed action envelope emitted by agents."""

    MOVE = "move"
    ATTACK = "attack"
    WAIT = "wait"
    INTERACT = "interact"


@dataclass(frozen=True)
class ActionSpec:
    """Declares action types an agent may emit."""

    allowed_types: Tuple[ActionType, ...]


@dataclass(frozen=True)
class PerceivedEntity:
    entity_id: str
    faction: str
    position: Tuple[int, int]
    hp: int
    max_hp: int
    tags: Tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentPerception:
    """Input format used by agent decision logic."""

    tick: int
    self_id: str
    self_kind: AgentKind
    self_position: Tuple[int, int]
    self_hp: int
    self_max_hp: int
    nearby_entities: Tuple[PerceivedEntity, ...] = ()
    visible_items: Tuple[str, ...] = ()
    map_notes: MappingLike = field(default_factory=dict)


@dataclass(frozen=True)
class AgentAction:
    """Decision output format emitted by agents."""

    actor_id: str
    action_type: ActionType
    target_id: Optional[str] = None
    destination: Optional[Tuple[int, int]] = None
    metadata: MappingLike = field(default_factory=dict)


@dataclass(frozen=True)
class AgentDecision:
    """Output container designed to support richer reasoning later."""

    action: AgentAction
    rationale: str
    confidence: float = 1.0


MappingLike = Dict[str, Any]


class DecisionPolicy(Protocol):
    """Hook for richer reasoning engines or LLM-backed policies later."""

    def decide(self, perception: AgentPerception, spec: ActionSpec) -> AgentDecision:
        ...


class Agent(Protocol):
    """Shared agent interface for players and NPCs."""

    agent_id: str
    kind: AgentKind
    action_spec: ActionSpec

    def think(self, perception: AgentPerception) -> AgentDecision:
        ...


class DeterministicPolicy:
    """Base policy hook with deterministic behavior.

    Subclasses implement deterministic decision logic now, and can later be
    replaced by richer model-based policies via the same protocol.
    """

    def decide(self, perception: AgentPerception, spec: ActionSpec) -> AgentDecision:
        if ActionType.WAIT not in spec.allowed_types:
            first = spec.allowed_types[0]
            return AgentDecision(
                action=AgentAction(actor_id=perception.self_id, action_type=first),
                rationale="fallback to first allowed action",
                confidence=0.2,
            )

        return AgentDecision(
            action=AgentAction(actor_id=perception.self_id, action_type=ActionType.WAIT),
            rationale="default deterministic wait",
            confidence=0.5,
        )


@dataclass
class RuntimeAgent:
    """Concrete agent wrapper around a pluggable decision policy."""

    agent_id: str
    kind: AgentKind
    action_spec: ActionSpec
    policy: DecisionPolicy

    def think(self, perception: AgentPerception) -> AgentDecision:
        decision = self.policy.decide(perception, self.action_spec)
        if decision.action.action_type not in self.action_spec.allowed_types:
            return AgentDecision(
                action=AgentAction(actor_id=self.agent_id, action_type=ActionType.WAIT),
                rationale=(
                    f"policy emitted disallowed action {decision.action.action_type}; "
                    "runtime coerced to WAIT"
                ),
                confidence=0.0,
            )
        return decision




class PlayerMirrorPolicy(DeterministicPolicy):
    """Deterministic player policy that mirrors server-provided intent."""

    def decide(self, perception: AgentPerception, spec: ActionSpec) -> AgentDecision:
        requested = perception.map_notes.get("requested_action")
        if isinstance(requested, str):
            try:
                action_type = ActionType(requested)
            except ValueError:
                action_type = None
            if action_type and action_type in spec.allowed_types:
                return AgentDecision(
                    action=AgentAction(
                        actor_id=perception.self_id,
                        action_type=action_type,
                        target_id=perception.map_notes.get("target_id"),
                        destination=perception.map_notes.get("destination"),
                    ),
                    rationale="mirror validated player input intent",
                    confidence=0.95,
                )
        return super().decide(perception, spec)


class MonsterAggroPolicy(DeterministicPolicy):
    """Sample monster behavior: attack closest non-monster; otherwise wander."""

    def decide(self, perception: AgentPerception, spec: ActionSpec) -> AgentDecision:
        enemies = [e for e in perception.nearby_entities if "monster" not in e.tags]
        if enemies and ActionType.ATTACK in spec.allowed_types:
            closest = min(enemies, key=lambda e: manhattan(perception.self_position, e.position))
            return AgentDecision(
                action=AgentAction(
                    actor_id=perception.self_id,
                    action_type=ActionType.ATTACK,
                    target_id=closest.entity_id,
                ),
                rationale=f"attack closest enemy {closest.entity_id}",
                confidence=1.0,
            )

        if ActionType.MOVE in spec.allowed_types:
            # Deterministic patrol step based on tick parity.
            dx = 1 if perception.tick % 2 == 0 else -1
            new_pos = (perception.self_position[0] + dx, perception.self_position[1])
            return AgentDecision(
                action=AgentAction(
                    actor_id=perception.self_id,
                    action_type=ActionType.MOVE,
                    destination=new_pos,
                ),
                rationale="no enemies; deterministic patrol",
                confidence=0.8,
            )

        return super().decide(perception, spec)


class VillagerRoutinePolicy(DeterministicPolicy):
    """Sample NPC behavior: interact with nearby players, else move between points."""

    waypoints: Tuple[Tuple[int, int], ...] = ((0, 0), (0, 1), (1, 1), (1, 0))

    def decide(self, perception: AgentPerception, spec: ActionSpec) -> AgentDecision:
        players = [e for e in perception.nearby_entities if e.faction == "players"]
        if players and ActionType.INTERACT in spec.allowed_types:
            target = sorted(players, key=lambda e: e.entity_id)[0]
            return AgentDecision(
                action=AgentAction(
                    actor_id=perception.self_id,
                    action_type=ActionType.INTERACT,
                    target_id=target.entity_id,
                    metadata={"dialogue": "greeting"},
                ),
                rationale=f"greet player {target.entity_id}",
                confidence=0.9,
            )

        if ActionType.MOVE in spec.allowed_types:
            idx = perception.tick % len(self.waypoints)
            return AgentDecision(
                action=AgentAction(
                    actor_id=perception.self_id,
                    action_type=ActionType.MOVE,
                    destination=self.waypoints[idx],
                ),
                rationale="follow deterministic routine",
                confidence=0.8,
            )

        return super().decide(perception, spec)


@dataclass
class ThinkResult:
    tick: int
    decisions: Dict[str, AgentDecision]


class AgentScheduler:
    """Deterministic scheduler for periodic agent thinking.

    The scheduler only asks agents to think and returns their decisions. It does
    not apply or mutate game state.
    """

    def __init__(self, think_interval_ticks: int = 1):
        if think_interval_ticks <= 0:
            raise ValueError("think_interval_ticks must be > 0")
        self.think_interval_ticks = think_interval_ticks
        self._agents: Dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        self._agents[agent.agent_id] = agent

    def unregister(self, agent_id: str) -> None:
        self._agents.pop(agent_id, None)

    def run_tick(self, tick: int, perceptions: MappingLike) -> ThinkResult:
        if tick % self.think_interval_ticks != 0:
            return ThinkResult(tick=tick, decisions={})

        decisions: Dict[str, AgentDecision] = {}
        for agent_id in sorted(self._agents):
            perception = perceptions.get(agent_id)
            if perception is None:
                continue
            decisions[agent_id] = self._agents[agent_id].think(perception)
        return ThinkResult(tick=tick, decisions=decisions)


def manhattan(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def build_default_agents() -> Sequence[RuntimeAgent]:
    """Sample setup with one NPC villager and one monster NPC agent."""

    npc_spec = ActionSpec((ActionType.MOVE, ActionType.INTERACT, ActionType.WAIT))
    monster_spec = ActionSpec((ActionType.MOVE, ActionType.ATTACK, ActionType.WAIT))

    villager = RuntimeAgent(
        agent_id="npc_villager_1",
        kind=AgentKind.NPC,
        action_spec=npc_spec,
        policy=VillagerRoutinePolicy(),
    )
    monster = RuntimeAgent(
        agent_id="monster_wolf_1",
        kind=AgentKind.NPC,
        action_spec=monster_spec,
        policy=MonsterAggroPolicy(),
    )
    player = RuntimeAgent(
        agent_id="player_1",
        kind=AgentKind.PLAYER,
        action_spec=ActionSpec((ActionType.MOVE, ActionType.ATTACK, ActionType.INTERACT, ActionType.WAIT)),
        policy=PlayerMirrorPolicy(),
    )
    return (player, villager, monster)
