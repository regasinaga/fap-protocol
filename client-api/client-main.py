from clientapi import ClientEntity
from threading import Thread

# this is a function callback. this function is called everytime
# TCPDataInd is called.
def demo_func(message_json):
	print(message_json["content"])

# init client entity object
client_name = "YOUR_NAME"
host = "localhost"
port = 9000
client = ClientEntity(client_name, demo_func)

# connecting
client.connReq(host, port)
client.connResp()
client.greet()

# run receiver threading
Thread(target=client.run).start()

# user can only send 5 message
for m in range(0, 5):
	receiver = input("receiver:\t")
	content = input("message:\n")
	client.TCPDataSend(receiver, content)
	
# disconnecting
client.disconnReq()
client.disconnResp()


	
	