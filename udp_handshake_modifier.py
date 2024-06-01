
import socket
import time
import random
import os


Cloudflare_IP = '188.114.97.73'
# Cloudflare_IP = '162.159.195.44'
# Cloudflare_IP = '162.159.192.161'
# Cloudflare_IP = '162.159.192.138'
# Cloudflare_IP = '188.114.99.108'
Cloudflare_port = 1014



localPort = 2500
remoteHost = Cloudflare_IP
remotePort = Cloudflare_port



num_noise = 1 # total number of udp noise packet
noise_length_min = 5  # min packet size in bytes
noise_length_max = 10 # max packet size in bytes

def send_random_data(sock, addr):
	
	for i in range(num_noise):
		k = random.randint(noise_length_min, noise_length_max)

		print("send noise payload",k,"bytes")

		# quic protocol
		# 'CE 00 00 00 01 08' + '8 byte ID' + '00 00 44 D0' + 'pkn' + 'payload'   
		# sock.sendto(bytes.fromhex('CB 00 00 00 01 08 0E 93 FC 2B FC C1 28 96 00 00 44 D0') + os.urandom(k) , addr)
		sock.sendto(bytes.fromhex('CE 00 00 00 01 08 3E 57 96 5F 4C 64 81 3A 00 00 44 D0') + os.urandom(k), addr)
		# sock.sendto(bytes.fromhex('C4 00 00 00 01 08 3E 57 96 5F 4C 64 81 3A 00 00 44 D0') + os.urandom(k), addr)
		# sock.sendto(bytes.fromhex('CD 00 00 00 01 08 3E 57 96 5F 4C 64 81 3A 00 00 44 D0') + os.urandom(k), addr)
		# sock.sendto(bytes.fromhex('CF 00 00 00 01 08 3E 57 96 5F 4C 64 81 3A 00 00 44 D0') + os.urandom(k), addr)
		# sock.sendto(bytes.fromhex('C8 00 00 00 01 08 0E 93 FC 2B FC C1 28 96 00 00 44 D0') + os.urandom(k) , addr) 

	print("finish")		




try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('', localPort))
except:
	print('Failed to bind on port ' + str(localPort))


knownClient = None
knownServer = (remoteHost, remotePort)
print('listening on '+str(localPort))


while True:
	data, addr = s.recvfrom(32768)
	if knownClient is None or addr != knownServer:
		send_random_data(s , knownServer)		
		knownClient = addr

	if addr == knownClient:
		s.sendto(data, knownServer)
		
	else:
		s.sendto(data, knownClient)




