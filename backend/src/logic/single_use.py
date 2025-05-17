from langchain.schema import SystemMessage, HumanMessage

from models.core_models import ChatRequest
from misc.prompts import system_prompt

async def RefineRequirement(req: ChatRequest, llm, db = None):
    lc_messages = [SystemMessage(content=system_prompt)] + [
        HumanMessage(content=m.content) if m.role == "user" else SystemMessage(content=m.content)
        for m in req.messages
    ]

    response = llm.invoke(lc_messages)
    lc_messages.append([SystemMessage(content=response.content)])

    if db:
        if not req.chat_uid:
            req.chat_uid = db.create_chat(lc_messages)
        else:
            db.update_chat(req.chat_uid, lc_messages)

    return {"chat_uid": req.chat_uid, "role": "assistant", "content": response.content}