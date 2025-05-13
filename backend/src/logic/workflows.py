from langgraph.graph import END, StateGraph, START

from models.state import CodeAndReviewGraphState
from logic.nodes import CodeAndReviewNodes

class code_and_review():
    def __init__(self, llm, max_iterations = 1, reflect = False):
        self.llm = llm
        self.max_iterations = max_iterations
        self.reflect = reflect
        self.compiled_workflow = None

    def compile(self):
        workflow = StateGraph(CodeAndReviewGraphState)
        code_and_review_nodes = CodeAndReviewNodes(self.max_iterations, self.reflect, self.llm)

        # Define the nodes
        workflow.add_node("generate", code_and_review_nodes.generate_code)  # generation solution
        workflow.add_node("check_code", code_and_review_nodes.review_code)  # check code
        workflow.add_node("reflect", code_and_review_nodes.reflect)  # reflect

        # Build graph
        workflow.add_edge(START, "generate")
        workflow.add_edge("generate", "check_code")
        workflow.add_conditional_edges(
            "check_code",
            code_and_review_nodes.decide_to_finish,
            {
                "end": END,
                "reflect": "reflect",
                "generate": "generate",
            },
        )
        workflow.add_edge("reflect", "generate")
        self.compiled_workflow = workflow.compile()
        return self.compiled_workflow