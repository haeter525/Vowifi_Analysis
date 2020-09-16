#!/usr/bin/python3

import random
import time
from socket import *

remote_ip = "127.0.0.1"
remote_port = 11223

# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Assign IP address and port number to socket
serverSocket.bind(('127.0.0.1', 12000))

while True:
    # Generate random number in the range of 0 to 10
    rand = random.randint(0, 10)

    print(f"Send {rand}")
    message = rand.to_bytes(5, 'big')

    serverSocket.sendto(message, (remote_ip, remote_port))

    time.sleep(1)

