import socket, threading
import math, random, time

# Variables

header = 64
ip = "192.168.122.169"
port = 5050
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

identifiers = {}

#

def reset():
    global ip, port, server, header
    global identifiers

    ip = ""
    port = 0
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    header = 64
    identifiers = {}

def start_server(ip_in, port_in):
    print("[!] Server Started")

    address = (ip_in, port_in)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(address)

    server.listen()

    while True: update(server, address)

#

def update(server, address):
    connection, address = server.accept()
    thread = threading.Thread(target=handle_client, args=(connection, address))
    thread.start()

    print(f"[i] Active Connections: {threading.active_count() - 1}")

def handle_client(connection, address):
    global identifiers

    print(f"[!] {address} Connected")
    send(connection, "msg", "Succesfully Connected!")
    identifiers[address[0]] = address[0]

    connected = True
    while connected:
        length = connection.recv(header).decode("utf-8")
        if length:
            length = int(length)
            message = connection.recv(length).decode("utf-8")

            if not ";" in message: continue

            print_out = ""
            message = message.split(";")
            match message[0]:
                case "sys":
                    match message[1]:
                        case "disconnect":
                            connected = False
                            print(f"[!] {identifiers[address[0]]} Disconnected")
                case "alias":
                    identifiers[address[0]] = message[1]
                    print_out = (f"Nickname Set {address[0]} -> {message[1]}")
                case "msg":
                    print_out = f"{identifiers[address[0]]}: {message[1]}"
                case "_": continue

            if print_out != "": print(f"[>] {print_out}")

def send(connection, type, message):
    message = f"{type};{message}"
    connection.send(message.encode("utf-8"))

#

# start_server(ip, port)