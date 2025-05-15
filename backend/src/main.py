from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import json

from models.core_models import ChatRequest, ChatMessage, PromptRequest, PreviewResponse, CodeGenerationRequest, CodeGenerationResponse, BlueprintRequest
from logic.single_use import RefineRequirement
from logic.workflows import code_and_review
from logic.nodes import blueprint_generator
from services.db import db

# Load credentials from .env file
load_dotenv()

app = FastAPI()

# CORS setup for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OS environments
CHAT_MODEL = os.getenv("CHAT_MODEL")
LLM_API_KEY = os.getenv("GOOGLE_API_KEY")
HOST_IP = os.getenv("HOST_IP") if os.getenv("HOST_IP") else "0.0.0.0"
PORT_NUMBER = int(os.getenv("PORT_NUMBER")) if os.getenv("PORT_NUMBER") else 8000 
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS")) if os.getenv("MAX_ITERATIONS") else 1
REFLECT = bool(os.getenv("REFLECT")) if os.getenv("REFLECT") else False
CONNECTION_STRING = os.getenv("CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")


# LLM setup (via LangChain)
llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0.3, google_api_key=LLM_API_KEY)

# DB setup
db_service = db(connection_string=CONNECTION_STRING, db_name=DB_NAME)

@app.post("/chat")
async def chat(req: ChatRequest):
    return await RefineRequirement(req, llm, db_service)

@app.post('/blueprint')
async def blueprint(req: BlueprintRequest):
    generator = blueprint_generator(llm=llm)
    generator = generator.build()

    # workaround for error pydantic_core._pydantic_core.ValidationError
    b = generator.invoke(req.message)
    return {"blueprint": json.loads(b.blueprint)}
    

@app.post("/build", response_model=CodeGenerationResponse)
async def generate_code(req: CodeGenerationRequest):
    workflow = code_and_review(llm, MAX_ITERATIONS, REFLECT, req.blueprint, req.message).compile()
    return workflow.invoke({"messages": [("user", req.message), ("user", str(req.blueprint))], "iterations": 0, "error": ""})

if __name__ == "__main__":
    uvicorn.run(app, host=HOST_IP, port=PORT_NUMBER)
