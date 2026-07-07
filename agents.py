import random; 

NAME_POOL = ["Akshar", "Bindu", "Chaitanya", "Damodar", "Eshwar", "Fanny", "Gauri", "Hari", "Ila", "Jaggu"]

ROLES = {
   "BK_ENG": 
      {
         "title": "Software Engineer", 
         "bias": "easier to implement & debug, modularity and resusability",
         "skill": "deep knowledge of backend systems, schemas, APIs. Good at execution."
      },
   "PM": 
      {"title": "Product Manager",
       "bias": "prioritization, timelines, accuracy, easier to modify later, concerned about the product in whole", 
       "skill": "cross-functional coordination, prioritization, result-oriented, concerned about the actual product and takes ownership"
      },
   "ARCT": 
      {
         "title": "Architect",
         "bias": "long-term maintainability, scalability and cost it will incur",
         "skill": "deep knowledge of system design, frameworks, scalability and architectural decisions"
      },
   "ENG_MGR": 
      {
         "title": "Engineering Manager",
         "bias": "decision making, best approach for the team, long-term vision, concerned about the team and their efforts",
         "skill": "team management, project planning, coordination, broad-level view, holds the power to make decisions for Engineering world"
      }
}

class Agent:
   def __init__(self, name, role_key, system_prompt, client): 
      # public attributes
      self.name = name
      self.role_key = role_key
      self.role_title = ROLES[role_key]["title"]
      self.system_prompt = system_prompt
      self.client = client

      # private attributes
      self._history = []   # this agent's own past turns; NOT on the Blackboard

   # ── Generate methods ───────────────────────────────────────────────────
   # Build user prompt, generate_stream(), yield chunks, save to pvt _history

   def propose_stream(self, business_ask: str):
      """Opening turn — independent position, no shared context yet."""
      user_prompt = (
         f"Business ask:\n{business_ask}\n\n"
         f"Give your initial position in 4-6 sentences: what you would do "
         f"and the one or two things you would insist on."
      )
      chunks = []
      try:
         for chunk in self.client.generate_stream(self.system_prompt, user_prompt):
            chunks.append(chunk)
            yield chunk
      finally:
         self._history.append("".join(chunks))

   def rebut_stream(self, business_ask: str, others_transcript: str):
      """Live discussion turn — sees shared transcript, can @mention or AGREE."""
      user_prompt = (
         f"Business ask:\n{business_ask}\n\n"
         f"Discussion so far:\n{others_transcript}\n\n"
         f"Your last position:\n{self._history[-1] if self._history else '(none yet)'}\n\n"
         f"Reply in 2-4 sentences. "
         f"Start with @Name: to address a teammate directly (they get the next turn). "
         f"Start with AGREE: if you are satisfied with where things stand."
      )
      chunks = []
      try:
         for chunk in self.client.generate_stream(self.system_prompt, user_prompt):
            chunks.append(chunk)
            yield chunk
      finally:
         self._history.append("".join(chunks))

   def synthesize_stream(self, business_ask: str, full_transcript: str):
      """ENG_MGR only — reads full transcript and produces the final ADR."""
      user_prompt = (
         f"Business ask:\n{business_ask}\n\n"
         f"Full team discussion:\n{full_transcript}\n\n"
         f"Write the final Architecture Decision Record with these exact sections:\n"
         f"## Decision\n## Context\n## Options Considered\n"
         f"## Tradeoffs & Risks\n## Unresolved Disagreement (if any)\n## Next Steps"
      )
      chunks = []
      # Guarantees _history.append() runs even if the LLM call errors partway through, so later turns don't crash on a missing history entry.
      try:
         for chunk in self.client.generate_stream(self.system_prompt, user_prompt):
            chunks.append(chunk)
            yield chunk
      finally:
         self._history.append("".join(chunks))


def build_panel(client, guardrails="") -> dict[str, Agent]:
      role_keys = ["BK_ENG", "PM", "ARCT", "ENG_MGR"]
      whitelisted_names = random.sample(NAME_POOL, len(role_keys))
      panel: dict[str, Agent] = {}
      
      for name, role_key in zip(whitelisted_names, role_keys):
         system_prompt = f"You are {name}, a {ROLES[role_key]['title']}. Your bias is {ROLES[role_key]['bias']}. Your skill is {ROLES[role_key]['skill']}. {guardrails}"
         panel[name] = Agent(name, role_key, system_prompt, client)

      return panel