from clientapi import ClientEntity

def demo_func(message_json):
	print(message_json["content"])
	
client_name = "YOUR_NAME"
client = ClientEntity(client_name, demo_func)
client.start()

while True:
	receiver = input("receiver\t:")
	content = input("content\t:")
	client.TCPDataSend(receiver, content)
	
	