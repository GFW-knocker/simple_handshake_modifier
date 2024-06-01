#!/usr/bin/env python3

import re
import socket
import threading
from pathlib import Path
import os
import copy
import time
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler


if os.name == 'posix':
    print('os is linux')
    import resource   # ( -> pip install python-resources )
    # set linux max_num_open_socket from 1024 to 128k
    resource.setrlimit(resource.RLIMIT_NOFILE, (127000, 128000))



listen_PORT = 2500    # pyprox listening to 127.0.0.1:listen_PORT

Cloudflare_IP = '188.114.97.73'   # plos.org (can be any cloudflare ip)
Cloudflare_port = 80


# ignore description below , its for old code , just leave it intact.
my_socket_timeout = 60 # default for google is ~21 sec , recommend 60 sec unless you have low ram and need close soon
first_time_sleep = 0.01 # speed control , avoid server crash if huge number of users flooding (default 0.1)
accept_time_sleep = 0.01 # avoid server crash on flooding request -> max 100 sockets per second



class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(128)  # up to 128 concurrent unaccepted socket queued , the more is refused untill accepting those.
        while True:
            client_sock , client_addr = self.sock.accept()                    
            client_sock.settimeout(my_socket_timeout)
            
            #print('someone connected')
            time.sleep(accept_time_sleep)   # avoid server crash on flooding request
            thread_up = threading.Thread(target = self.my_upstream , args =(client_sock,) )
            thread_up.daemon = True   #avoid memory leak by telling os its belong to main program , its not a separate program , so gc collect it when thread finish
            thread_up.start()
            

    def my_upstream(self, client_sock):
        first_flag = True
        backend_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_sock.settimeout(my_socket_timeout)
        backend_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)   #force localhost kernel to send TCP packet immediately (idea: @free_the_internet)

        while True:
            try:
                if( first_flag == True ):                        
                    first_flag = False

                    time.sleep(first_time_sleep)   # speed control + waiting for packet to fully recieve
                    data = client_sock.recv(16384)
                    #print('len data -> ',str(len(data)))                
                    #print('user talk :')

                    if data:                                                                    
                        backend_sock.connect((Cloudflare_IP,Cloudflare_port))
                        thread_down = threading.Thread(target = self.my_downstream , args = (backend_sock , client_sock) )
                        thread_down.daemon = True
                        thread_down.start()
                        # backend_sock.sendall(data)    
                        send_modified_http_header(data,backend_sock)

                    else:                   
                        raise Exception('cli syn close')

                else:
                    data = client_sock.recv(4096)
                    if data:
                        backend_sock.sendall(data)
                    else:
                        raise Exception('cli pipe close')
                    
            except Exception as e:
                #print('upstream : '+ repr(e) )
                time.sleep(2) # wait two second for another thread to flush
                client_sock.close()
                backend_sock.close()
                return False



            
    def my_downstream(self, backend_sock , client_sock):
        first_flag = True
        while True:
            try:
                if( first_flag == True ):
                    first_flag = False            
                    data = backend_sock.recv(16384)
                    if data:
                        client_sock.sendall(data)
                    else:
                        raise Exception('backend pipe close at first')
                    
                else:
                    data = backend_sock.recv(4096)
                    if data:
                        client_sock.sendall(data)
                    else:
                        raise Exception('backend pipe close')
            
            except Exception as e:
                #print('downstream '+backend_name +' : '+ repr(e)) 
                time.sleep(2) # wait two second for another thread to flush
                backend_sock.close()
                client_sock.close()
                return False




def send_modified_http_header(data , sock):  
    print(data)

    # host_string = re.findall(b"\r\nHost:(.*)\r\n", data)[0] 
    # print(host_string)

    new_data = new_data.replace(b"Go-http-client/1.1",b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    print(new_data)
    sock.sendall(new_data)
    print('----------finish------------')




print ("Now listening at: 127.0.0.1:"+str(listen_PORT))
ThreadedServer('',listen_PORT).listen()



    
