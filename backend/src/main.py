from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages.utils import convert_to_messages
from dotenv import load_dotenv
import os
import json

from fastapi import WebSocket, WebSocketDisconnect
import asyncio

from models.core_models import ChatRequest, CodeGenerationRequest, BlueprintRequest
from logic.single_use import RefineRequirement
from logic.workflows import architect_code_review_workflow
from logic.nodes import blueprint_generator
from services.db import db
import misc.prompts as prompt
from services.auth import verify_api_token, verify_ws_token

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
    

@app.post("/build", response_model=dict)
async def generate_code(req: CodeGenerationRequest, user_token=Depends(verify_api_token)):
    prompts = {
        "architect_prompt": prompt.backend_architect_prompt,
        "engineer_prompt": prompt.backend_engineer_prompt,
        "engineer_retry_prompt": prompt.backend_engineer_retry_prompt,
        "reviewer_prompt": prompt.backend_reviewer_prompt
    }
    workflow = architect_code_review_workflow(llm, prompts=prompts, max_iterations=3).compile()
    return await workflow.ainvoke(
        {
            "messages": [("user", req.message), ("user", str(req.blueprint))], 
            "iterations": 0, 
            "error": "",
            "confidence_score": 0, 
            "specs": "",
            "requirements": f"{req.message}\n {req.blueprint}"
        })

@app.websocket("/ws/code-generation")
async def websocket_code_generation(websocket: WebSocket):
    auth_header = websocket.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        await websocket.close(code=1008)
        return

    token = auth_header[7:]  # Strip 'Bearer '

    if not verify_ws_token(token):
        await websocket.close(code=1008)
        return
    
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()
            user_message = data.get("message")
            blueprint = data.get("blueprint")

            async def send_update(message: str):
                await websocket.send_json({"status": "update", "message": message})

            prompts = {
                "architect_prompt": prompt.backend_architect_prompt,
                "engineer_prompt": prompt.backend_engineer_prompt,
                "engineer_retry_prompt": prompt.backend_engineer_retry_prompt,
                "reviewer_prompt": prompt.backend_reviewer_prompt
            }

            # Pass send_update to workflow constructor
            workflow = architect_code_review_workflow(
                llm, prompts=prompts, max_iterations=3, send_update=send_update
            ).compile()

            await workflow.ainvoke({
                "messages": [("user", user_message), ("user", str(blueprint))],
                "iterations": 0,
                "error": "",
                "confidence_score": 0,
                "specs": "",
                "requirements": f"{user_message}\n{blueprint}"
            })

            await websocket.send_json({"status": "complete", "confidence_score": result.confidence_score, "full_history": result.messages})

    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host=HOST_IP, port=PORT_NUMBER)
