#!/usr/bin/env python
import socket
import sys
import threading
import subprocess

CMD="fswebcam --no-banner -d /dev/video0 /dev/stdout"

lock = None

class Handler(threading.Thread):
	def __init__(self, con, addr):
		super(Handler, self).__init__()
		self.con = con
		self.addr = addr
	def run(self):
		lock.acquire()
		proc = subprocess.Popen(CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		proc.wait()
		lock.release()
		data = proc.communicate()[0]
		self.con.send(data)
		self.con.close()

def main(args):
	if len(args) < 2:
		print "[!] Usage: {} [port]".format(args[0])
		sys.exit(1)
	port = int(args[1])
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(("0.0.0.0", port))
	sock.listen(8888)
	global lock
	lock = threading.Lock()
	try:
		while True:
			con, addr = sock.accept()
			print "[*] Connection from {}:{}".format(addr[0], addr[1])
			handler = Handler(con, addr)
			handler.start()
	except KeyboardInterrupt:
		print "Shutting down..."
	except EOFError:
		print "Shutting down..."
	sock.close()

if __name__ == '__main__':
	main(sys.argv)