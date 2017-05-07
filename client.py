import socket
import sys
import threading
import json
from time import time 

class ClientEntity():
	def __init__(self, name, gui=None):
		self.name = name
		self.csap = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.gui = gui
		self.connected = False
		
	def connReq(self, hostaddr, hostport):
		print('conn req')
		self.csap.connect((hostaddr, hostport))
		
	def connResp(self):
		print('con resp')
		
		self.gui.append_text('[SERVER > ME]' + '\n' + 'connected to server')
		self.connected = True
		
	def TCPDataSend(self, receiver, message_content):
		print('data send')
		message_str = '{"context":"TCPDataInd","content":"' + message_content + '","receiver":"'+ receiver + '"}'
		self.gui.append_text('[ME > '+receiver+']'+ '\n' + message_content)
		self.csap.send(message_str.encode('utf-8'))
		
	def TCPDataInd(self, message_json):
		print('data ind')
		sender = message_json["sender"]
		content = message_json["content"]
		appendthis = '[' + sender + ' > ME ]\n' + content
		self.gui.append_text(appendthis)
		
	def TCPDataConf(self):
		print('data conf')
		message_str = '{"context":"TCPDataResp","content":"' + str(time()) + '","receiver":"server"}'
		self.csap.send(message_str.encode('utf-8'))
		
	def TCPDataResp(self):
		print('data resp')
		
	def disconnReq(self):
		print('disconn req')
		message_str = '{"context":"disconnInd","content":"' + str(time()) + '","receiver":"'+self.name+'","status":"not read"}'
		self.csap.send(message_str.encode('utf-8'))
		
	def disconnResp(self):
		print('disconn resp')
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
