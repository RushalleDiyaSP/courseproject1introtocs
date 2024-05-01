from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import socket

# Load server's public key
try:
    with open("server_public.pem", "r") as file:
        server_public_key = RSA.import_key(file.read())
except Exception as e:
    print("Error loading server public key:", e)
    exit(1)

def encrypt_message(message, public_key):
    cipher = PKCS1_OAEP.new(public_key)
    ciphertext = cipher.encrypt(message.encode())
    return ciphertext

def main():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect(('localhost', 12346))
        
        item_data = server_socket.recv(1024).decode()
        print("Received item data from server:", item_data)
        
        item_number = input("Enter the item number you wish to purchase: ")
        name = input("Enter your name: ")
        credit_card_number = input("Enter your credit card number: ")
        
        # Encrypt customer data
        encrypted_customer_data = encrypt_message("||".join([item_number, name, credit_card_number]), server_public_key)
        
        # Send encrypted data to server
        server_socket.sendall(encrypted_customer_data)
        
        response = server_socket.recv(1024).decode()
        if response == "1":
            print("Your order is confirmed.")
        else:
            print("Credit card transaction is unauthorized.")
        
        server_socket.close()
    except Exception as e:
        print("An error occurred during execution:", e)

if __name__ == "__main__":
    main()
