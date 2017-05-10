from pymongo import *
import json 
class DBHandler:
	def __init__(self, mongohost, mongoport=27017, db="chat", collection="msg_history"):
		self.client = MongoClient(mongohost, mongoport)
		self.db = self.client[db]
		self.col = self.db[collection]
		
	def save_message(self, message_json):
		self.col.insert_one(message_json)
		
	def load_not_read(self, user):
		msgs = self.col.find({"status":"not read", "receiver":user}, {'_id': False});
		return msgs
		
	def mark_as_read(self, user):
		self.col.update_many({"receiver":user},{"$set": {"status":"read"}})
