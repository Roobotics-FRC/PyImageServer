#!/usr/bin/env python
import socket
import sys
import threading
import subprocess

THREADED=False

class Handler(threading.Thread):
	def __init__(self, con, addr):
		super(Handler, self).__init__()
		self.con = con
		self.addr = addr
	def run(self):
		proc = subprocess.Popen("fswebcam --no-banner -d /dev/video0 /dev/stdout", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		proc.wait()
		data = proc.communicate()[0]
		buf = self.con.recv(1024)
		while not buf.endswith('\r\n\r\n'):
			print repr(buf)
			buf += self.recv(1024)
		self.con.send("HTTP/1.1 200 OK\r\n")
		self.con.send("Server: RooImage v1.0\r\n")
		self.con.send("Content-Type: image/jpeg\r\n")
		self.con.send("Content-Length: {}\r\n".format(len(data)))
		self.con.send("\r\n")
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
	try:
		while True:
			con, addr = sock.accept()
			print "[*] Connection from {}:{}".format(addr[0], addr[1])
			handler = Handler(con, addr)
			handler.start() if THREADED else handler.run()
	except KeyboardInterrupt:
		print "Shutting down..."
	except EOFError:
		print "Shutting down..."
	sock.close()

if __name__ == '__main__':
	main(sys.argv)
