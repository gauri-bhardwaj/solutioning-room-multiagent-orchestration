import re
import logging

from agents import Agent
from blackboard import Blackboard

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


class SolutioningRoom:
    def __init__(self, agents: dict, max_turns: int = 12):
        self.agents = agents
        self.max_turns = max_turns

        self.participants = list(agents.keys())
        self.blackboard = Blackboard(max_entries=max_turns)

        # Search for ENG_MGR who will generate the ADR 
        self.manager_name = next(
            (name for name, agent in agents.items() if agent.role_key == "ENG_MGR"),
            None
        )

        # Build the @mention regex from THIS run's actual names.
        escaped_names = "|".join(re.escape(n) for n in self.participants)
        self._mention_re = re.compile(
            rf"^@({escaped_names})\s*:?", re.IGNORECASE
        )
        self._agree_re = re.compile(r"^agree\s*:?", re.IGNORECASE)

    def run_stream(self, business_ask: str):
        # First event: the roster.
        # The frontend needs to know the cast to build the 4 UI lanes (one per agent) in advance.
        yield {
            "phase": "roster",
            "agents": [
                {
                    "name": name,
                    "role": self.agents[name].role_key,
                    "role_title": self.agents[name].role_title,
                }
                for name in self.participants
            ],
        }

        turn = 0

        # ── Phase 1: Opening round ────────────────────────────────────────
        # Each agent states their position independently — no one sees anyone else's take yet. This prevents anchoring: whoever speaks first would otherwise pull everyone's position toward theirs.
        logger.info("Opening round — order: %s", self.participants)
        for name in self.participants:
            turn += 1
            agent = self.agents[name]

            yield {"phase": "turn_start", "turn": turn, "agent": name}

            chunks = []
            for chunk in agent.propose_stream(business_ask):
                chunks.append(chunk)
                yield {"phase": "delta", "turn": turn, "agent": name, "delta": chunk}

            full_text = "".join(chunks)
            self.blackboard.add(turn, name, full_text)
            yield {"phase": "opening", "turn": turn, "agent": name, "content": full_text}

        # ── Phase 2: Live discussion ──────────────────────────────────────
        # Round-robin by default.
        #   @Name: — jump the queue; that person speaks next.
        #   AGREE: — signal convergence; when everyone's MOST RECENT turn
        #            was an AGREE, the debate is over (true consensus).
        logger.info("Discussion starting")
        queue = list(self.participants)
        idx = 0
        agreed: set = set()   # tracks who has agreed in their LAST turn

        while turn < self.max_turns and len(agreed) < len(self.participants):
            name = queue[idx % len(queue)]
            idx += 1
            turn += 1
            agent = self.agents[name]

            # Each agent sees the shared transcript minus their own lines (they already have their own turns in private _history).
            others_view = self.blackboard.transcript(exclude_agent=name)

            yield {"phase": "turn_start", "turn": turn, "agent": name}

            chunks = []
            for chunk in agent.rebut_stream(business_ask, others_view):
                chunks.append(chunk)
                yield {"phase": "delta", "turn": turn, "agent": name, "delta": chunk}

            full_text = "".join(chunks)
            self.blackboard.add(turn, name, full_text)
            yield {"phase": "discussion", "turn": turn, "agent": name, "content": full_text}

            stripped = full_text.strip()

            # Convergence check — AGREE adds to set, any substantive reply removes from set (they've re-entered the debate).
            if self._agree_re.match(stripped):
                agreed.add(name)
            else:
                agreed.discard(name)

            # @mention check — jump the queue so the named person goes next.
            mention = self._mention_re.match(stripped)
            if mention:
                raw = mention.group(1)
                # Resolve back to the correctly-cased name in our participants.
                target = next(
                    (p for p in self.participants if p.lower() == raw.lower()),
                    None
                )
                if target and target != name:
                    idx = queue.index(target)  # next loop iteration picks target

        if turn >= self.max_turns:
            logger.info("Hit max_turns (%d) — moving to synthesis", self.max_turns)

        # ── Phase 3: Synthesis ────────────────────────────────────────────
        # ENG_MGR reads the full transcript and writes the final ADR.
        logger.info("Synthesis — %s drafting ADR", self.manager_name)
        turn += 1
        manager = self.agents[self.manager_name]
        full_transcript = self.blackboard.full_transcript()

        yield {"phase": "turn_start", "turn": turn, "agent": self.manager_name}

        chunks = []
        for chunk in manager.synthesize_stream(business_ask, full_transcript):
            chunks.append(chunk)
            yield {"phase": "delta", "turn": turn, "agent": self.manager_name, "delta": chunk}

        adr = "".join(chunks)
        yield {"phase": "synthesis", "turn": turn, "agent": self.manager_name, "content": adr}
