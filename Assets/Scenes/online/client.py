import socket, threading
import math, random, time

# Variables

host_ip = "192.168.1.10"
host_port = 5050

player_identifiers = []

#

def reset():
    global host_ip, host_port, player_identifiers

    host_ip = ""
    host_port = 0

    player_identifiers = []