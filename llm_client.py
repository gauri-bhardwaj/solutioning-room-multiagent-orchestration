import os;
class LLMClient:
   def __init__(self, provider="mock", model="claude-sonnet-4-6"):
      self.provider = provider
      self.model = model
      if self.provider == "anthropic" and not os.environ.get("ANTHROPIC_API_KEY"):
         raise ValueError("Missing required environment variable: ANTHROPIC_API_KEY")
      elif provider == "mock": 
         pass 
      else:
         raise ValueError(f"Invalid provider: {provider}. System has not been built for this provider yet. Please use 'mock' for now.")
      
   def generate_stream(self, system_prompt: str, user_content: str):
      if self.provider == "mock":
         yield "MOCK RESPONSE 1"
         yield "MOCK RESPONSE 2"
         yield "MOCK RESPONSE 3"
      elif self.provider == "anthropic":
         raise NotImplementedError("anthropic provider not built yet")
      
