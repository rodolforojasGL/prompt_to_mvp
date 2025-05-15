from pymongo import MongoClient
from bson.objectid import ObjectId 

class db():
    def __init__(self, connection_string, db_name):
        self.connection_string = connection_string
        self.db_name = db_name
        assert(self.connection_string != None and self.db_name != None)
        self.client = self.setup_client()

    def setup_client(self):
        client = MongoClient(self.connection_string)
        return client[self.db_name]
    
    def create_chat(self, conversation):
        return str(self.client.chat.insert_one({"conversation": str(conversation)}).inserted_id)
    
    def update_chat(self, id, conversation) -> None: 
        query_filter = {"_id": ObjectId(id)}
        replace_document = {"conversation": str(conversation)}
        self.client.chat.replace_one(query_filter, replace_document)
        