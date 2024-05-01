import socket

def main():
    item_data = ""
    with open("items.txt", "r") as file:
        item_data = file.read()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12346))  # Change the port number here
    server_socket.listen(1)
    print("Server is listening...")
    
    while True:
        conn, addr = server_socket.accept()
        with conn:
            print('Connected by', addr)
            conn.sendall(item_data.encode())

if __name__ == "__main__":
    main()
