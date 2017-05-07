from tkinter import *
import socket
import threading
from client import ClientEntity
import logging
		
class WidgetLogger(logging.Handler):
	def __init__(self, widget):
		logging.Handler.__init__(self)
		self.widget = widget

	def emit(self, record):
		self.widget.insert(INSERT, record + '\n')
		
class ClientGUI:
	def __init__(self):
		
		self.main_gui = Tk()
		self.text_host = None
		self.text_port = None
		self.text_user = None
		self.btn_connect = None
		self.btn_send = None
		self.btn_disconnect = None
		self.text_message = None
		self.text_receiver = None
		self.client_entity = None
		self.text_recv = None
		self.wd = None
		
		self.init_component()
		
	def start(self):
		self.main_gui.mainloop()
		
	def init_component(self):
		self.main_gui.minsize(width=500, height=450)
		self.main_gui.resizable(width=False, height=False)

		self.text_host = Text(self.main_gui, width=20, height=1)
		self.text_host.insert(INSERT, "127.0.0.1")
		self.text_host.grid(row=0, column=0)

		self.text_port = Text(self.main_gui, width=20, height=1)
		self.text_port.insert(INSERT, "9000")
		self.text_port.grid(row=0, column=1)

		self.text_user = Text(self.main_gui, width=20, height=1)
		self.text_user.insert(INSERT, "username1")
		self.text_user.grid(row=1, column=0)

		self.btn_connect = Button(self.main_gui, text="connect", width=20, height=1, command=self.connect_callback)
		self.btn_connect.grid(row=2, column=0)

		self.text_message = Text(self.main_gui, width=40, height=1)
		self.text_message.grid(row=3, column=0, columnspan=2, rowspan=2)
		
		self.text_receiver = Text(self.main_gui, width=40, height=1)
		self.text_receiver.grid(row=5, column=0, columnspan=2, rowspan=2)

		self.btn_send = Button(self.main_gui, text="send", width=10, height=1, command=self.send_callback)
		self.btn_send.grid(row=5, column=2)

		self.text_recv = Text(self.main_gui, width=40, height=20)
		self.text_recv.grid(row=7, column=0, columnspan=2, rowspan=10)
		
		self.btn_disconnect = Button(self.main_gui, text="disc", width=10, height=1, command=self.disconnect_callback)
		self.btn_disconnect.grid(row=20, column=0)
		
		self.wd = WidgetLogger(self.text_recv)
		
		self.text_recv.config(state=DISABLED)
		self.text_host.config(state=NORMAL)
		self.text_port.config(state=NORMAL)
		self.text_user.config(state=NORMAL)
		self.text_message.config(state=DISABLED)
		
	def connect_callback(self):
		try:
			host = self.text_host.get("1.0", END)
			port = self.text_port.get("1.0", END)
			user = self.text_user.get("1.0", END)
			
			self.client_entity = ClientEntity(user, gui=self)
			self.client_entity.connReq(host, int(port))
			self.client_entity.connResp()
			self.client_entity.greet()
			threading.Thread(target=self.client_entity.run).start()
			
			self.text_host.config(state=DISABLED)
			self.text_port.config(state=DISABLED)
			self.text_user.config(state=DISABLED)
			self.text_message.config(state=NORMAL)
			self.text_recv.config(state=NORMAL)
			self.text_receiver.config(state=NORMAL)
			
			self.btn_connect.config(state=DISABLED)
			self.btn_disconnect.config(state=NORMAL)
			
		except socket.gaierror:
			self.append_text('connection refused')
		except ConnectionRefusedError:
			self.append_text('connection refused')
			
	def disconnect_callback(self):
		self.client_entity.disconnReq()
		self.btn_connect.config(state=NORMAL)
		self.text_recv.config(state=DISABLED)
		self.text_host.config(state=NORMAL)
		self.text_port.config(state=NORMAL)
		self.text_user.config(state=NORMAL)
		self.text_message.config(state=DISABLED)
		
	def send_callback(self):
		receiver = self.text_message.get("1.0", END)
		message_str = self.text_receiver.get("1.0", END)
		
		self.client_entity.TCPDataSend(receiver, message_str)
		self.client_entity.TCPDataResp()
		
	def append_text(self, message):
		
		self.text_recv.config(state=NORMAL)
		self.wd.emit(message)
		self.text_message.focus_set()
		self.text_recv.config(state=DISABLED)
