import socket, threading
import math, random, time

# Variables

header = 64
host_ip = "192.168.122.169"
host_port = 5050

connected = False

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#

def reset(data):
    global host_ip, host_port, header, socket

    host_ip = data[0]
    host_port = data[1]
    header = 64

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#

def connect(alias):
    global connected
    
    try:
        socket.connect((host_ip, host_port))
        connected = True
        send("alias", alias)
    except:
        print("[!] Unable to Connect to Server")

def disconnect():
    send("sys", "disconnect")
    exit()

#

def send(type, content):
    message = f"{type};{content}"
    message = message.encode("utf-8")
    message_len = len(message)
    send_len = str(message_len).encode("utf-8")
    send_len += b' ' * (header - len(send_len))
    
    socket.send(send_len)
    socket.send(message)

def update():
    global connected

    message = socket.recv(2048).decode("utf-8")

    if message:
        if not ";" in message: return

        print_out = ""
        message = message.split(";")
        match message[0]:
            case "sys":
                match message[1]:
                    case "kick":
                        print(f"[!] Kicked from Server")
                        connected = False
            case "msg":
                print_out = message[1]
            case "_": return
        
        print(f"[>] {print_out}")

# connect("John")
# send("msg", "fuh")

# while connected: update()

# send("sys", "disconnect")
