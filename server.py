import socket
import threading
import random

configs = [
    ["00A0000000", "1111100020", "0010002020", "011100222B", "0000002020", "0000000020", "0003330000", "0000300000", "0033333000", "0000C00000"],
    ["000A000000", "0001100020", "0010002020", "0111002B2B", "0000020020", "0000020000", "0003330000", "0000300000", "0033333000", "00000C0000"],
    ["0000A00000", "0001100020", "0010002020", "011100222B", "0000002020", "0000000020", "0003330000", "0000C00000", "0033333000", "0000300000"],
    ["000000A000", "1111100020", "0010002020", "011100222B", "0000002020", "0000000020", "0003330000", "0000300000", "0033333C00", "0000000000"],
    ["00000000A0", "1111100020", "0010002020", "011100222B", "0000002020", "0000000020", "0003330000", "0000300000", "0033333000", "0000C00000"],
    ["0000000A00", "1111100020", "0010002020", "011100222B", "0000002020", "0000000020", "0003330000", "0000300000", "0033333000", "0000000C00"],
    ["000000A000", "1111100020", "0010002020", "011100222B", "0000002020", "0000000020", "0003330000", "0000C00000", "0033333000", "0000300000"],
    ["00000A0000", "1111100020", "0010002020", "011100222B", "0000002020", "0000000020", "0003330000", "0000300000", "0033333000", "00000000C0"],
    ["0000A00000", "1111100020", "0010002020", "011100222B", "0000002020", "0000000020", "0003330000", "0000300000", "0033333000", "0C00000000"],
    ["00A0000000", "1111100020", "0010002020", "011100222B", "0000002020", "0000000020", "0003330000", "0000300000", "0033333000", "00C0000000"]
]

def check_hit(board, row, col, planes_hit):
    if board[row][col] in ['A', 'B', 'C']:
        planes_hit += 1
        if planes_hit == 3:
            return 'Ai castigat', planes_hit
        return 'X', planes_hit  # Avion doborat
    elif board[row][col] in ['1', '2', '3']:
        return '1', planes_hit  # Parte a avionului atinsa
    else:
        return '0', planes_hit  # Niciun avion atins



def handle_client(conn, addr, board):
    global sender_conn
    sender_conn = conn
    print(f"Conexiune nouă de la {addr}")
    conn.send(b"Bine ati venit! Introduceti un nume unic pentru a va identifica:")

    while True:
        client_name = conn.recv(1024).decode().strip()
        if client_name in client_names:
            conn.send(b"Numele este deja folosit. Introduceti un alt nume.")
        else:
            print(f"Clientul {addr} s-a identificat ca '{client_name}'")
            client_names.add(client_name)
            break

    conn.send(b"Introduceti coordonatele pentru a trage (ex: 5 3)")

    # Configuratie random
    board = random.choice(configs)
    print(f"Configurație pentru clientul {client_name}:")
    for row in board:
        print(row)

    planes_hit = 0

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            row, col = map(int, data.split())

            #daca randul si coloana sunt in interiorul dimensiunii tablei
            if row < 0 or row >= len(board) or col < 0 or col >= len(board[0]):
                conn.send(b"Coordonatele sunt in afara matricei. Incercati din nou.")
                continue

            hit, planes_hit = check_hit(board, row, col, planes_hit)
            conn.send(hit.encode())

            if hit == 'X':
                print(f"Clientul {client_name} a doborât un avion!")

            #  daca toate cele 3 avioane au fost doborate
            if hit == 'Ai castigat':
                print(f"Clientul {client_name} a câștigat jocul!")
                conn.send(b"Felicitari! Ati castigat jocul!")
                
                # Trimite mesajul
                message = f"Utilizatorul {client_name} a castigat meciul!"
                broadcast(message)
                
                # Alege o noua configuratie
                board = random.choice(configs)
                print("Configurație nouă:")
                for row in board:
                    print(row)
                planes_hit = 0  # reseteaza contorul pentru noul joc

        except ValueError:
            message = "Format invalid. Încercați din nou."
            conn.send(message.encode('utf-8'))

    print(f"Conexiunea cu {client_name} a fost închisă.")
    conn.close()
    clients.remove(conn)
    client_names.remove(client_name)

# Functie pentru a difuza un mesaj catre toti clientii
def broadcast(message):
    for client in clients:
        client.send(message.encode('utf-8'))

# Configurarea serverului
HOST = 'localhost'
PORT = 8000
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Serverul așteaptă conexiuni pe {HOST}:{PORT}")

# Alege o configurație initiala
current_board = random.choice(configs)
print("Configurație inițială:")
for row in current_board:
    print(row)

#Lista clienti
clients = []
client_names = set()
threads = []

# loop accepta conexiuni
while True:
    conn, addr = server_socket.accept()
    clients.append(conn)
    thread = threading.Thread(target=handle_client, args=(conn, addr, current_board))
    thread.start()
    threads.append(thread)