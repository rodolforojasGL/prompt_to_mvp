from langchain_core.prompts import ChatPromptTemplate

from models.core_models import BlueprintOutputClass

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
