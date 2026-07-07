# The Solutioning Room

A multi-agent system that simulates an engineering design review. Paste in a business problem — four AI agents debate it live in the browser, then the Engineering Manager writes a structured Architecture Decision Record (ADR).

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green) ![Anthropic](https://img.shields.io/badge/Anthropic-Claude-orange)

---

## What it does

1. You describe a technical or product problem.
2. Four agents — Backend Engineer, Product Manager, Architect, Engineering Manager — each state an independent opening position (no anchoring bias).
3. They debate in real time, @mentioning each other and signalling `AGREE:` when satisfied.
4. When consensus is reached (or the turn cap hits), the Engineering Manager synthesises a final ADR.
5. Every agent's response streams token-by-token into its own lane in the browser via SSE.

Agents are grounded in shared guardrails (compliance, engineering standards, definition of done) appended to every system prompt — the "constitution" pattern.

---

## Architecture

```
Browser (EventSource)
    ↕ SSE  GET /stream?ask=...
FastAPI  (main.py)
    ↓
SolutioningRoom  (orchestrator.py)   ← control flow only, no LLM calls
    ↓
Agent × 4  (agents.py)              ← propose / rebut / synthesize
    ↓
LLMClient  (llm_client.py)          ← provider adapter (mock | anthropic)
    ↑
Blackboard  (blackboard.py)         ← shared transcript (drop-oldest, max 12 entries)
```

Key design decisions:

- **Generator pipeline throughout** — `LLMClient` → `Agent` → `Orchestrator` → `StreamingResponse`. No buffering; tokens reach the browser as they arrive.
- **Blackboard vs `_history`** — shared memory (what agents said out loud) vs private memory (an agent's own past turns). Agents see others' transcript, not others' reasoning.
- **Anchoring bias prevention** — opening round is independent; no agent sees anyone else's position before stating their own.
- **@mention queue jumping** — an agent can address a teammate directly; the orchestrator re-routes the next turn to that person.
- **Convergence via `set`** — AGREE adds to the set; any substantive reply discards the agent. Done when `len(agreed) == len(participants)`.

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.11, FastAPI, uvicorn |
| Streaming | Server-Sent Events (SSE) |
| LLM | Anthropic Claude (via REST) or mock |
| Frontend | Vanilla JS, no framework |

---

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/YOUR_USERNAME/solutioning-room.git
cd solutioning-room
pip install -r requirements.txt

# 2. Set your API key
cp .env.example .env
# edit .env and add your ANTHROPIC_API_KEY

# 3. Run
python main.py
# open http://localhost:8000
```

To run without an API key, select **mock** in the provider dropdown — agents return placeholder text so you can verify the full pipeline works before spending any credits.

---

## Project structure

```
agents.py            Agent class + build_panel() — roles, biases, generate methods
blackboard.py        Shared transcript with drop-oldest trimming
llm_client.py        Provider adapter — mock and anthropic backends
orchestrator.py      SolutioningRoom — three-phase control flow, no LLM calls
guardrails_loader.py Loads guardrails/*.md into one string for system prompts
main.py              FastAPI server — two routes: / and /stream
index.html           Frontend — 4-lane live view, SSE consumer
guardrails/          Policy docs appended to every agent's system prompt
requirements.txt
```

---

## Deploying for a live demo

1. Push this repo to GitHub.
2. Sign up at [render.com](https://render.com) → New Web Service → connect the repo.
3. **Build command**: `pip install -r requirements.txt`
4. **Start command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add `ANTHROPIC_API_KEY` as an environment variable in the Render dashboard.
6. In `index.html`, set `anthropic` as the default selected provider so visitors get live AI responses.

Each full discussion run costs under $0.05 with `claude-sonnet-4-6`.

---

## What's next

- `solutioning-room-langgraph/` — a second version using LangGraph for agent routing, conditional branching, and native checkpointing.
- Real Anthropic streaming in `llm_client.py` (mock → live API).
- Session persistence via Redis so discussions survive tab closes.
- Unit tests in `tests/test_orchestrator_logic.py`.
