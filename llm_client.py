import os

class LLMClient:
   def __init__(self, provider="mock", model="claude-sonnet-4-6"):
      self.provider = provider
      self.model = model
      if provider == "mock":
         pass
      elif provider == "anthropic":
         if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ValueError("Missing required environment variable: ANTHROPIC_API_KEY")
      else:
         raise ValueError(f"Invalid provider: {provider}. Supported: 'mock', 'anthropic'.")

   def generate_stream(self, system_prompt: str, user_content: str):
      if self.provider == "mock":
         yield "MOCK RESPONSE 1"
         yield "MOCK RESPONSE 2"
         yield "MOCK RESPONSE 3"

      elif self.provider == "anthropic":
         import anthropic
         client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
         # .stream() keeps the HTTP connection open and yields text chunks
         # as they arrive — same contract as the mock provider above.
         with client.messages.stream(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
         ) as stream:
            for text in stream.text_stream:
               yield text
