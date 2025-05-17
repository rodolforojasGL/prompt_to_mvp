from langchain.schema import SystemMessage, HumanMessage
import os
from typing import Annotated
from typing import TypedDict
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from misc.prompts import system_prompt, blueprint_prompt, sales_analyzer_prompt, business_analyst_prompt
from models.core_models import ChatRequest, ChatMessage
load_dotenv()

CHAT_MODEL = os.getenv("CHAT_MODEL")
LLM_API_KEY = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=0.3, google_api_key=LLM_API_KEY)

class State(TypedDict):
    # messages have the type "list".
    # The add_messages function appends messages to the list, rather than overwriting them
    messages: Annotated[list, add_messages]
req = ChatRequest(messages=[ChatMessage(role="user", content="Hello")])
lc_messages = [SystemMessage(content=sales_analyzer_prompt)]  
for m in req.messages:
    if m.role == "user":
        lc_messages.append(HumanMessage(content=m.content))
    else:
        lc_messages.append(SystemMessage(content=m.content))

def chatbot(state: State):
    return {"messages": [llm.invoke(lc_messages)]}
'''The first argument is the unique node name
# The second argument is the function or object that will be called whenever the node is used.'''

class MyGraphState(TypedDict):
  count: int
  msg: str


class mvp_analizer_workflow():
    def __init__(self, llm, max_iterations = 1, reflect = False):
        self.llm = llm
        self.max_iterations = max_iterations
        self.reflect = reflect
        self.compiled_workflow = None

    def compile(self):
            
        # Create an instance of StateGraph with the structure of MyGraphState
        workflow = StateGraph(MyGraphState)

        sales_analist_node_name = "Sales Analist"
        bussines_analist_node_name = "Businnes Analist"
        software_architect_analist_node_name = "Software Architect Analist"

        # Add three nodes to the workflow which are replicas of "counter"
        workflow.add_node(sales_analist_node_name, chatbot)
        workflow.add_node(bussines_analist_node_name, chatbot)
        workflow.add_edge(START, sales_analist_node_name)
        workflow.add_edge(sales_analist_node_name, bussines_analist_node_name)
        workflow.add_edge(bussines_analist_node_name, END)
        self.compiled_workflow = workflow.compile()
        
        try:
            plt.imsave("C:\\Users\\Gnomeus\\Downloads\\Sofi\\saved_image.jpg", workflow.get_graph().draw_mermaid_png())
        except Exception as a:
            pass
        
        return self.compiled_workflow
        

def counter(state: MyGraphState):
  state["count"] += 1
  state["msg"] = f"Counter function has been called {state['count']} time(s)"
  return state
