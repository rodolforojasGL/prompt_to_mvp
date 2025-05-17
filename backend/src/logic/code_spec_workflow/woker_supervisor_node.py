from typing import List, Optional, Literal, Union
from langchain_core.language_models.chat_models import BaseChatModel

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command
from langchain_core.messages import HumanMessage, trim_messages
from typing_extensions import TypedDict
from langchain_anthropic import ChatAnthropic


class CodeSpecState(MessagesState):
    next: str
    api_spec: str


def make_supervisor_node(llm: BaseChatModel,members: list[str]) -> str:
    options = ['FINISH'] + members


    def supervisor_node(state: CodeSpecState) -> Command[Literal[*members, '__end__']]:
        """LLM based supervisor router worker"""

        goto = determine_next_worker(state)
        
        return Command(goto=goto, update={"next": goto})
    
    return supervisor_node

def determine_next_worker(state: CodeSpecState) -> str:
    if  'api_spec' in state and  (state['api_spec'] is not None or state['api_spec'] != ""):
        return END
    else:
        return 'api_specification_generator'