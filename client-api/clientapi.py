import socket
import sys
import threading
import json
from time import time
from datetime import datetime as dt

class ClientEntity():
	def __init__(self, name, callback):
		self.name = name
		self.csap = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connected = False
		self.callback = callback
		
	def connReq(self, hostaddr, hostport):
		print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> connReq")
		self.csap.connect((hostaddr, hostport))
		
	def connResp(self):
		print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> connResp")
		self.connected = True
		
	def TCPDataSend(self, receiver, message_content):
		try:
			message_str = '{"context":"TCPDataInd","content":"' + message_content + '","receiver":"'+ receiver + '"}'
			print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> TCPDataSend ")
			print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> " + message_content)
			self.csap.send(message_str.encode('utf-8'))
			
		except ConnectionResetError:
			print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> connection reset")
		except ConnectionRefusedError:
			print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> connection refused")
			self.disconnResp()
			
	def TCPDataInd(self, message_json):
		print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> TCPDataInd")
		sender = message_json["sender"]
		content = message_json["content"]
		self.callback(message_json)
		
	def TCPDataConf(self):
		print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> TCPDataConf")
		message_str = '{"context":"TCPDataResp","content":"' + str(time()) + '","receiver":"server"}'
		self.csap.send(message_str.encode('utf-8'))
		
	def TCPDataResp(self):
		print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> TCPDataResp")
		
	def disconnReq(self):
		print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> disconnReq")
		message_str = '{"context":"disconnInd","content":"' + str(time()) + '","receiver":"'+self.name+'","status":"not read"}'
		self.csap.send(message_str.encode('utf-8'))
		
	def disconnResp(self):
		print(dt.now().strftime("%d %b %Y - %H:%M:%S") + " >> disconnResp")
		self.csap.close()
		
	def greet(self):
		self.TCPDataSend("inbox", self.name)
		
	def run(self):
		while True:
			try:
				message_byte = self.csap.recv(1024)
				message_str = message_byte.decode('utf-8').split('[--END--]')
				
				for message in message_str:
					message_json = json.loads(message)
					self.trigger_primitives(message_json)
				
			except ValueError:
				pass
			except ConnectionResetError:
				break
			except OSError:
				break
				
	def trigger_primitives(self, message_json):

		if(message_json['context'] == "TCPDataInd"):
			self.TCPDataInd(message_json)
			self.TCPDataConf()
		elif(message_json['context'] == "TCPDataResp"):
			self.TCPDataResp()
		elif(message_json['context'] == "disconnResp"):
			self.disconnResp()
			
	
	def stop(self):
		self.csap.close()
		