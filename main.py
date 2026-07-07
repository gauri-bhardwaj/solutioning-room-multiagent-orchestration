import json
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse

from agents import build_panel
from guardrails_loader import load_guardrails
from llm_client import LLMClient
from orchestrator import SolutioningRoom

# load the anthropic API key 
load_dotenv()

app = FastAPI()

# for index.html & static assets 
@app.get("/")
def serve_ui():
    return FileResponse("index.html")

# stream the discussion events back to the browser as they happen, instead of waiting - SSE (FastAPI)
@app.get("/stream")
def stream(
    ask: str,
    provider: str = "anthropic",
    model: str = "claude-sonnet-4-6",
    max_turns: int = 12,
):
    """ Build a new panel & then stream SSE events back to the browser until the ADR is done. """
    
    def generate():
        # Build a fresh panel for every run so names are re-randomised and no state leaks between requests.
        client = LLMClient(provider=provider, model=model)
        guardrails = load_guardrails()
        panel = build_panel(client, guardrails)
        room = SolutioningRoom(panel, max_turns=max_turns)

        #   The double newline is the event terminator — the browser's EventSource API uses it to know where one event ends and the next begins.
        for event in room.run_stream(ask):
            yield f"data: {json.dumps(event)}\n\n"

    # media_type="text/event-stream" tells the browser this is an SSE
    return StreamingResponse(generate(), media_type="text/event-stream")

# Initiation 
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
