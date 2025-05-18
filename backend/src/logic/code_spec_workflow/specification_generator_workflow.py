from langchain_core.messages import HumanMessage, SystemMessage
from langchain_anthropic import ChatAnthropic
from woker_supervisor_node import CodeSpecState, make_supervisor_node
from langgraph.types import Command
from typing import List, Optional, Literal, Union
from langgraph.graph import StateGraph,START, END
from dotenv import load_dotenv
import os 

load_dotenv()

ANTHROPIC_CHAT_MODEL = os.getenv("ANTHROPIC_CHAT_MODEL")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") 

anthropic_llm = ChatAnthropic(model_name=ANTHROPIC_CHAT_MODEL, temperature=0.0, api_key=ANTHROPIC_API_KEY)


def web_api_specification_generator_node(state: CodeSpecState) -> Command[Literal['supervisor']] :
    """Generate REST API endpoint specifications based on requirements"""
    
    # Get requirements from state
    requirements = state.get("requirements", "")
    
    # Create prompt for API spec generation
    prompt_message = [

        SystemMessage(content= f"""
                      You're a software developer with experience in Python and Flask API. You return technical information about web endpoint specification,  don't be conversational.
                      you must provide the following details in the specification
                      
                      - HTTP METHOD
                      - URL PATH
                      - PATH VARIABLES
                      - QUERY PARAMS
                      - HTTP STATUS CODES 
                      - REQUEST EXAMPLE
                      - RESPONSE EXAMPLE
                    """),

        HumanMessage(content=f"""
        Given the following requirements, generate a detailed list of RESTful API endpoint specifications.
        For each endpoint, include:
        - HTTP method (GET, POST, PUT, DELETE etc)
        - URL path
        - Request parameters/body schema
        - Response schema
        - Brief description of the endpoint's purpose

        Requirements:
        {requirements}

         You must format the api specification as YML format optimized the output result to use as less lines as possible, use \n to break lines. it should be be suitable to generate Swagger API documentation
        """)
    ]

    # Add prompt to existing messages
    messages = state["messages"] + prompt_message
    
    # Get response from LLM
    response = anthropic_llm.invoke(messages)
    updated_response_only_yaml_spec = clear_out_llm_respone(response.content)
    
    # Return command to go back to supervisor with updated messages
    return Command(
        goto="supervisor",
        update={
            "messages": [
                 HumanMessage(content=response.content, name="specs")
            ],
            "api_spec": updated_response_only_yaml_spec
        }
    )

api_spec_generator_supervisor_node = make_supervisor_node(anthropic_llm,["api_specification_generator"])

doc_spec_builder = StateGraph(CodeSpecState)
doc_spec_builder.add_node("supervisor", api_spec_generator_supervisor_node)
doc_spec_builder.add_node("api_specification_generator", web_api_specification_generator_node)

# define edges
doc_spec_builder.add_edge(START, "supervisor")
doc_spec_generator_graph = doc_spec_builder.compile()

def clear_out_llm_respone(respone: str) -> str:
    """Remove yaml text from the beginning of the response"""
    # Clone response to avoid modifying original
    clone_response = respone[:]
    
    # Find and remove ```yaml from anywhere in the string
    # Find and remove ```yaml
    if "```yaml" in clone_response:
        clone_response = clone_response.replace("```yaml", "")
    
    # Find and remove closing ```
    if "```" in clone_response:
        clone_response = clone_response.replace("```", "")
        
    return clone_response.strip()

if __name__ == "__main__":

    user_prompt = """
Functional Requirements for Todo Application
Based on your idea, here are the functional requirements for a todo application with user authentication:
2. Task Management
    * The system shall allow authenticated users to create new tasks
    * The system shall require a title for each task
    * The system shall allow optional description for each task
    * The system shall automatically associate tasks with the authenticated user
    * The system shall allow users to view all their tasks
    * The system shall allow users to view a specific task by ID
    * The system shall allow users to update the title of their tasks
    * The system shall allow users to update the description of their tasks
    * The system shall allow users to mark tasks as completed
    * The system shall allow users to mark completed tasks as incomplete
    * The system shall allow users to delete their tasks
    * The system shall prevent users from accessing or modifying tasks that don't belong to them
    """

    for s in doc_spec_generator_graph.stream(
    {"messages": [("user", user_prompt)]},
    {"recursion_limit": 100},
):
        print(s)
        if 'api_specification_generator' in s:
            with open("file_api.yml", "w") as f:
                f.write(clear_out_llm_respone(s['api_specification_generator']['messages'][0].content))
