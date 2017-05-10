from clientapi import ClientEntity

# this is a function callback. this function is called everytime
# TCPDataInd is called.

def demo_func(message_json):
	print(message_json["content"])
	
# for thread name
client_name = "YOUR_NAME"
client = ClientEntity(client_name, demo_func)

# start another thread
client.start()

while True:
	receiver = input("receiver\t:")
	content = input("content\t:")
	client.TCPDataSend(receiver, content)
	
	