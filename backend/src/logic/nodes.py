from langchain_core.prompts import ChatPromptTemplate

from models.state import architect_code_review_graph_state
from models.core_models import BlueprintOutputClass, BackendCodeSchema

class blueprint_generator():
    def __init__(self, llm) -> None:
        self.llm = llm

    def build(self):
        print("GENERATING BLUEPRINT")

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """<instructions> You are a software architect that translates user app ideas into structured application blueprints. 
                        Given a user description of an app, return a JSON object with:
                        - entities: list of main objects (e.g. object 1, object 2)
                        - relations: relationship between entities (e.g. user has many tasks)
                        - features: list of requested features (e.g. feature 1, feature 2, feature 3)
                        - endpoints: list of endpoints that satisfy all features (e.g. endpoint 1, endpoint 2, endpoint 3)
                        - pages: list of pages needed </instructions> \n Here the app idea:""",
                ),
                (
                    "user", "{input}"
                ),
            ]
        )
        structured_llm = self.llm.with_structured_output(BlueprintOutputClass)

        return prompt | structured_llm 

class CodeAndReviewNodes():
    def __init__(self, max_iterations, reflect_flag, llm, blueprint, summary):
        self.max_iterations = max_iterations
        self.reflect_flag = reflect_flag
        self.llm = llm
        self.blueprint = blueprint
        self.summary = summary

    def generate_code(self, state: architect_code_review_graph_state):

        print("GENERATING CODE")

        # State
        messages = state["messages"]
        iterations = state["iterations"]
        error = state["error"]

        if iterations == 0:
            prompt = [
                        ("system",
                        """<instructions> You are a senior Python engineer that translates user requirements and project blueprints into a simple Flask backend.
                            Given a project blueprint with the following structure:
                            {{
                                "entities": [list of main objects (e.g. object 1, object 2)]
                                "relations": [relationship between entities (e.g. user has many tasks)]
                                "features": [list of requested features (e.g. feature 1, feature 2, feature 3)]
                                "endpoints": [list of endpoints that satisfy all features (e.g. endpoint 1, endpoint 2, endpoint 3)]
                                "pages": [list of pages needed]
                            }}
                            And a project summary provided by the user. 
                            Create a simple Flask backend with endpoints that satisfies the application blueprint and the project summary.
                            I will provide you first with the project blueprint and then with the summary.
                        """)
                    ]
            messages = prompt + messages

        # We have been routed back to generation with an error
        if error == True:
            messages += [
                (
                    "user",
                    "Now, try again. Invoke the code tool to structure the output with a prefix, imports, and code block:",
                )
            ]

        # Solution
        
        structured_output_llm = self.llm.with_structured_output(BackendCodeSchema)
        code_solution = structured_output_llm.invoke(messages)
        messages += [
            (
                "assistant",
                f"{code_solution.prefix} \n Imports: {code_solution.imports} \n Code: {code_solution.code}",
            )
        ]

        # Increment
        iterations = iterations + 1
        return {"generation": code_solution, "messages": messages, "iterations": iterations}

    def review_code(self, state: architect_code_review_graph_state):

        print("REVIEWING CODE")

        # State
        messages = state["messages"]
        code_solution = state["generation"]
        iterations = state["iterations"]

        imports = code_solution.imports
        code = code_solution.code

        # Check imports
        try:
            exec(imports)
        except Exception as e:
            print("CODE IMPORT CHECK FAILED")
            error_message = [("user", f"Your solution failed the import test: {e}")]
            messages += error_message
            return {
                "generation": code_solution,
                "messages": messages,
                "iterations": iterations,
                "error": True,
            }

        # Check execution
        try:
            exec(imports + "\n" + code)
        except Exception as e:
            print("CODE BLOCK CHECK FAILED")
            error_message = [("user", f"Your solution failed the code execution test: {e}")]
            messages += error_message
            return {
                "generation": code_solution,
                "messages": messages,
                "iterations": iterations,
                "error": True,
            }

        # No errors
        print("NO TEST ERRORS")
        return {
            "generation": code_solution,
            "messages": messages,
            "iterations": iterations,
            "error": False,
        }

    def reflect(self, state: architect_code_review_graph_state):

        print("GENERATING SOLUTION")

        # State
        messages = state["messages"]
        iterations = state["iterations"]
        code_solution = state["generation"]

        # Prompt reflection

        # Add reflection
        reflections = self.llm.invoke(
            {"messages": messages}
        )
        messages += [("assistant", f"Here are reflections on the error: {reflections}")]
        return {"generation": code_solution, "messages": messages, "iterations": iterations}

    def decide_to_finish(self, state: architect_code_review_graph_state):
        error = state["error"]
        iterations = state["iterations"]

        if error == True or iterations == self.max_iterations:
            print("DECISION: FINISH")
            return "end"
        else:
            print("DECISION: RE-TRY")
            if self.reflect_flag == True:
                return "reflect"
            else:
                return "generate"