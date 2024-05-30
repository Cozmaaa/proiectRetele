import socket
import threading

# Configurarea clientului
HOST = 'localhost'
PORT = 8000

# Functie pentru primirea mesajelor de la server
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                print(message)
        except ConnectionAbortedError:
            break

# Functie pentru trimiterea mesajelor catre server
def send_messages():
    while True:
        coordinates = input(">")
        client_socket.send(coordinates.encode())
        if coordinates.lower() == 'quit':
            break


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# bun venit și introdu numele unic
print(client_socket.recv(1024).decode())
client_name = input("Introduceți un nume unic: ")
client_socket.send(client_name.encode())


receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()


send_thread = threading.Thread(target=send_messages)
send_thread.start()


send_thread.join()
receive_thread.join()


client_socket.close()