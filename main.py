from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from agent.agentic_workflow import GraphBuilder
from utils.save_to_document import save_document
from starlette.responses import JSONResponse
import os
import datetime
from dotenv import load_dotenv
from pydantic import BaseModel
import requests

# Load environment variables at the top
load_dotenv()

# Create the FastAPI app instance
app = FastAPI()

# --- THIS IS THE CRITICAL FIX ---
# Add the CORS middleware right after creating the app instance
# This tells your backend to accept requests from any domain ("*")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://ai-travel-planner-frontend.onrender.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- END OF FIX ---


# Define the request model
class QueryRequest(BaseModel):
    question: str



@app.get("/")
async def root():
    return {"message": "Backend is live"}
@app.post("/query")

@app.post("/query")
async def query(req: Request):
    data = await req.json()
    question = data.get("question", "")
    return {"answer": f"Your AI travel plan for '{question}' is ready!"}


# Define your API endpoint
@app.post("/query")
async def query_travel_agent(query: QueryRequest):
    try:
        print(f"Received query: {query.question}")
        graph = GraphBuilder(model_provider="groq")
        react_app = graph()

        # Note: Writing files to disk on services like Render is ephemeral
        # This graph image will disappear on the next deploy or server restart.
        try:
            png_graph = react_app.get_graph().draw_mermaid_png()
            with open("my_graph.png", "wb") as f:
                f.write(png_graph)
            print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
        except Exception as e:
            print(f"Warning: Could not save graph image. {e}")

        messages = {"messages": [query.question]}
        output = react_app.invoke(messages)

        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content  # Last AI response
        else:
            final_output = str(output)
        
        return {"answer": final_output}
    except Exception as e:
        print(f"Error during query processing: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})
