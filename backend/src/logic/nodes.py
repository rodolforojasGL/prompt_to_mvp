from models.state import CodeAndReviewGraphState

class CodeAndReviewNodes():

    def __init__(self, max_iterations, reflect_flag, llm):
        self.max_iterations = max_iterations
        self.reflect_flag = reflect_flag
        self.llm = llm

    def generate_code(self, state: CodeAndReviewGraphState):

        print("GENERATING CODE")

        # State
        messages = state["messages"]
        iterations = state["iterations"]
        error = state["error"]

        # We have been routed back to generation with an error
        if error == True:
            messages += [
                (
                    "user",
                    "Now, try again. Invoke the code tool to structure the output with a prefix, imports, and code block:",
                )
            ]

        # Solution
        code_solution = self.llm.invoke(
            {"messages": messages}
        )
        messages += [
            (
                "assistant",
                f"{code_solution.prefix} \n Imports: {code_solution.imports} \n Code: {code_solution.code}",
            )
        ]

        # Increment
        iterations = iterations + 1
        return {"generation": code_solution, "messages": messages, "iterations": iterations}

    def review_code(self, state: CodeAndReviewGraphState):

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

    def reflect(self, state: CodeAndReviewGraphState):

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

    def decide_to_finish(self, state: CodeAndReviewGraphState):
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