from typing import Annotated
from typing import TypedDict
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
load_dotenv()
class RefineWorkflowState(TypedDict):
    messages: Annotated[list, add_messages]


class refine_workflow():
    def __init__(self, llm, max_iterations = 1, reflect = False):
        self.llm = llm
        self.max_iterations = max_iterations
        self.reflect = reflect
        self.compiled_workflow = None
        self.checkpointer= None

    def compile(self):
            
        # Create an instance of StateGraph with the structure of MyGraphState
        workflow = StateGraph(RefineWorkflowState)

        sales_analist_node_name = "Sales Analist"
        # LLM setup (via LangChain)
        def chatbot(state: RefineWorkflowState):
            response = self.llm.invoke(state["messages"])
            return {"messages": [response]}
        
        #NODES
        workflow.add_node(sales_analist_node_name, chatbot)

        #EDGES
        workflow.add_edge(START, sales_analist_node_name)
        memory = MemorySaver()
        self.compiled_workflow = workflow.compile(checkpointer=memory, interrupt_before=None, interrupt_after=None, debug=True)
        
        return self.compiled_workflow
