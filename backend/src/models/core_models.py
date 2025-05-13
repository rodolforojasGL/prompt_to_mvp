from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class PromptRequest(BaseModel):
    messages: List[ChatMessage]

class PreviewResponse(BaseModel):
    blueprint: dict
    previews: List[str]

class CodeGenerationRequest(BaseModel):
    blueprint: dict
    layoutChoice: int

class CodeGenerationResponse(BaseModel):
    projectUrl: str

class BackendCodeSchema(BaseModel):
    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")