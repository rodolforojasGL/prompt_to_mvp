from langchain.schema import SystemMessage, HumanMessage

from logic.lang_workflows.mvp_refiner_workflow import refine_workflow
from models.core_models import ChatRequest
from misc.prompts import system_prompt, sales_analyzer_prompt
from dotenv import load_dotenv
import os
load_dotenv()

MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS")) if os.getenv("MAX_ITERATIONS") else 1
REFLECT = bool(os.getenv("REFLECT")) if os.getenv("REFLECT") else False


async def RefineRequirement(req: ChatRequest, llm):
    graph = refine_workflow(llm, MAX_ITERATIONS, REFLECT).compile()
    lc_messages = [SystemMessage(content=sales_analyzer_prompt)]  
    for m in req.messages:
        if m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        else:
            lc_messages.append(SystemMessage(content=m.content))

    config = {"configurable": {"thread_id": "1"}}
    events = graph.stream({"messages":lc_messages}, config=config )
    
    try:
        graph.get_graph().print_ascii()
    except Exception as a:
        pass

    for event in events:
        if "Sales Analist" in event:
            for value in event.values():
                msg = value["messages"][-1].content
                return {"role": "assistant", "content": msg}
            

# PREVIOUS VERSION OF THE REFINE REQUIREMENT
# async def RefineRequirement(req: ChatRequest, llm, db = None):
#     lc_messages = [SystemMessage(content=system_prompt)] + [
#         HumanMessage(content=m.content) if m.role == "user" else SystemMessage(content=m.content)
#         for m in req.messages
#     ]

#     response = llm.invoke(lc_messages)
#     lc_messages.append([SystemMessage(content=response.content)])

#     if db:
#         if not req.chat_uid:
#             req.chat_uid = db.create_chat(lc_messages)
#         else:
#             db.update_chat(req.chat_uid, lc_messages)

#     return {"chat_uid": req.chat_uid, "role": "assistant", "content": response.content}