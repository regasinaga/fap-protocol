import socket
import threading
import json
from time import time, sleep
from dbhandler import DBHandler

class ServerEntity(threading.Thread):
	def __init__(self, host, port, dbhost="localhost", dbport=27017):
		threading.Thread.__init__(self)
		self.ssap = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.ssap.bind((host, port))
		self.ssap.listen(1)
		self.client_handlers = dict()
		
		self.dbhandler = DBHandler(mongohost=dbhost, mongoport=dbport)
		print('listening on ',port)
		
	def run(self):
		while True:
			ssap, addr = self.ssap.accept()
			self.connInd(ssap)
			self.connConf(ssap)
			
	def connInd(self, ssap):
		print('new connection')
		client_handler = ClientHandlerThread(self, ssap)
		client_handler.start()
	
	def connConf(self, ssap):
		print('confirm connection')
		message_str = '{"context":"connResp","content":"","sender":"server","status":"read"}' + '[--END--]'
		ssap.send(message_str.encode('utf-8'))
		
	def TCPDataInd(self, sender, receiver, message_str):
		print(sender,' has sent new message')
		message_str = self.prepare_message(sender, receiver, message_str)
		self.dbhandler.save_message(json.loads(message_str))
		self.TCPDataSend(receiver, message_str)
	
	def TCPDataConf(self, sender):
		message_str = '{"context":"TCPDataResp","content":"' + str(time()) + '","sender":"server","status":"read"}' + '[--END--]'
		self.client_handlers[sender].send(message_str.encode('utf-8'))
		
	def TCPDataSend(self, receiver, message_str):
		try:
			self.client_handlers[receiver].send(message_str + '[--END--]')
			self.dbhandler.mark_as_read(receiver)
		except KeyError:
			print(receiver,' is not online yet')
			
	def TCPDataResp(self, receiver):
		print(receiver,' has received the message')
	
	def disconnInd(self, client):
		print(client,' wants to disconnect')
		self.disconnConf(client)
		
	def disconnConf(self, client):
		message = '{"context":"disconnResp","content":"' + str(time()) + '","sender":"server"}' + '[--END--]'
		
		self.client_handlers[client].stop()
		del self.client_handlers[client]
		
	def handle_greet(self, new_name, client):
		print(new_name,' has new inbox')
		self.client_handlers[new_name] = client
		
		msgs = self.dbhandler.load_not_read(new_name)
		print(new_name,' has ',msgs.count(),' new messages ')
		for msg in msgs:
			msg = json.dumps(msg)
			self.TCPDataSend(new_name, msg)
			
		self.dbhandler.mark_as_read(new_name)
		
	def prepare_message(self, sender, receiver, content):
		message_json = {
			"context":"TCPDataInd",
			"sender":sender,
			"receiver":receiver,
			"content":content,
			"status":"not read"
		}
		
		message_str = json.dumps(message_json)
		return message_str
		
class ClientHandlerThread(threading.Thread):
	def __init__(self, server, sock, chunk_size=256):
		threading.Thread.__init__(self)
		self.ssap = sock
		self.chunk_size = chunk_size
		self.server = server
		self.connected = True
		self.name = None
		
	def trigger_primitives(self, message_json):
		if message_json["context"] == "TCPDataInd":
			if message_json["receiver"] == "inbox":
				old_name = self.name
				self.name = message_json["content"]
				self.server.handle_greet(self.name, self)
			else:
				self.server.TCPDataInd(self.name, message_json["receiver"], message_json["content"])
		
		elif message_json["context"] == "TCPDataResp":
			self.server.TCPDataResp(self.name)
			
		elif message_json["context"] == "disconnInd":
			self.server.disconnInd(self.name)
	
	def get_name(self):
		return self.name
		
	def send(self, message_str):
		self.ssap.sendall(message_str.encode('utf-8'))
		
	def run(self):
		while self.connected:
			try:
				message_byte = self.ssap.recv(self.chunk_size)
				message_str = message_byte.decode('utf-8').replace("\n","")
 
				message_json = json.loads(message_str)
				self.trigger_primitives(message_json)
			
			except ValueError:
				pass
				
			except OSError:
				break
				
			except ConnectionResetError:
				break
			
	def stop(self):
		self.ssap.close()
		self.connected = False
	
if __name__ == "__main__":
	try:
		serv = ServerEntity("0.0.0.0", 9000)
		serv.start()
	except KeyboardInterrupt:
		exit()