from langchain.schema import SystemMessage, HumanMessage
from typing import List, Optional


from models.core_models import ChatRequest, ChatMessage
from misc.prompts import system_prompt, blueprint_prompt

async def RefineRequirement(req: ChatRequest, llm, db):
    lc_messages = [SystemMessage(content=system_prompt)] + [
        HumanMessage(content=m.content) if m.role == "user" else SystemMessage(content=m.content)
        for m in req.messages
    ]

    response = llm.invoke(lc_messages)
    lc_messages.append([SystemMessage(content=response.content)])

    if not req.chat_uid:
        req.chat_uid = db.create_chat(lc_messages)
    else:
        db.update_chat(req.chat_uid, lc_messages)

    return {"chat_uid": req.chat_uid, "role": "assistant", "content": response.content}


async def generate_blueprint_from_chat(messages: List[ChatMessage], llm) -> dict:

    lc_messages = [SystemMessage(content=blueprint_prompt)] + [
        HumanMessage(content=m.content) if m.role == "user" else SystemMessage(content=m.content)
        for m in messages
    ]

    response = llm.invoke(lc_messages)
    try:
        json_start = response.content.find("{")
        blueprint_str = response.content[json_start:]
        blueprint = eval(blueprint_str)
        return blueprint
    except Exception as e:
        return {"error": "Failed to parse blueprint", "raw": response.content, "exception": str(e)}