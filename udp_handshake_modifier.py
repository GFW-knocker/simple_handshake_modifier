
import socket
import time
import random
import os


Cloudflare_IP = '188.114.97.73'
# Cloudflare_IP = '188.114.96.158'
# Cloudflare_IP = '162.159.195.44'
# Cloudflare_IP = '162.159.192.171'
# Cloudflare_IP = '162.159.192.97'
# Cloudflare_IP = '162.159.192.138'
# Cloudflare_IP = '188.114.99.108'
Cloudflare_port = 928



localPort = 2500
remoteHost = Cloudflare_IP
remotePort = Cloudflare_port



num_noise = 1 # total number of udp noise packet
payload_length_min = 10  # min packet size in bytes
payload_length_max = 30 # max packet size in bytes

def send_random_data(sock, addr):
	
	for i in range(num_noise):
		k = random.randint(payload_length_min, payload_length_max)

		print("send noise payload",k,"bytes")

		# quic protocol
		# 'C9 00 00 00 01 08' + '8 byte ID' + '00 00 44 D0' + 'C3' + 'payload'
		# 'CB 00 00 00 01 08' + '8 byte ID' + '00 00 44 D0' + 'E4' + 'payload'  
		# 'C3 00 00 00 01 08' + '8 byte ID' + '00 00 44 D0' + '5D' + 'payload'  
		# 'C9 00 00 00 01 08' + '8 byte ID' + '00 00 44 D0' + 'AD' + 'payload'
		# 'C0 00 00 00 01 08' + '8 byte ID' + '00 00 44 D0' + '95' + 'payload'  
		# 'C2 00 00 00 01 08' + '8 byte ID' + '00 00 44 D0' + '61' + 'payload' 


		# quic work
		# 'CE 00 00 00 01 08' + '8 byte ID' + '00 00 44 D0' + 'payload'   #quic L=1292
		cb = random.randint(192,207)   # C0 to CF
		sock.sendto( cb.to_bytes() + bytes.fromhex('00 00 00 01 08') + os.urandom(8) + bytes.fromhex('00 00 44 D0') + os.urandom(k), addr)


		# STUN NOT WORK
		# '00 01 00 64 21 12 a4 42' + payload     #STUN L=162
		# sock.sendto( bytes.fromhex('00 01 00 64 21 12 a4 42') + os.urandom(k), addr)


		# DTLS NOT WORK
		# '16 fe fd 00 00 00 00 00 00 00 00 00 9d 01 00 00 91 00 00 00 00 00 00 00 91 fe fd' + payload   # DTLS L=199
		# sock.sendto( bytes.fromhex('16 fe fd 00 00 00 00 00 00 00 00 00 9d 01 00 00 91 00 00 00 00 00 00 00 91 fe fd') + os.urandom(k), addr)
		

		# SRTP NOT WORK
		# 'b0 61 00 01 00 00 00 00 00 00 00 00 be de 00 01 31 00 01 00' + payload   # DTLS L=79
		# sock.sendto( bytes.fromhex('b0 61 00 01 00 00 00 00 00 00 00 00 be de 00 01 31 00 01 00') + os.urandom(k), addr)
		

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




