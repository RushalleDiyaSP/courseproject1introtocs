from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import socket
import traceback

# Load bank's private key
with open("bank_private.pem", "r") as file:
    bank_private_key = RSA.import_key(file.read())

# Load server's public key
with open("server_public.pem", "r") as file:
    server_public_key = RSA.import_key(file.read())

# Load creditinfo data from file
def load_creditinfo():
    creditinfo = {}
    with open("creditinfo.txt", "r") as file:
        for line in file:
            name, hashed_card, available_credits = line.strip().split()
            creditinfo[name] = (hashed_card, int(available_credits))
    return creditinfo

# Function to update available credits in creditinfo file
def update_creditinfo(name, new_available_credits, credit_card_number):
    creditinfo = load_creditinfo()
    hashed_card = hash(credit_card_number)
    if name in creditinfo and creditinfo[name][0] == str(hashed_card):
        creditinfo[name] = (creditinfo[name][0], new_available_credits)
        with open("creditinfo.txt", "w") as file:
            for name, (hashed_card, available_credits) in creditinfo.items():
                file.write(f"{name} {hashed_card} {available_credits}\n")

# Sign data using bank's private key
def sign(data):
    h = SHA256.new(data)
    signer = PKCS1_v1_5.new(bank_private_key)
    signature = signer.sign(h)
    return signature

# Verify signature using server's public key
def verify_signature(data, signature, public_key):
    h = SHA256.new(data)
    verifier = PKCS1_v1_5.new(public_key)
    return verifier.verify(h, signature)

# Validate transaction
def validate_transaction(name, credit_card_number, item_price):
    creditinfo = load_creditinfo()
    hashed_card = hash(credit_card_number)
    if name in creditinfo and creditinfo[name][0] == str(hashed_card) and creditinfo[name][1] >= item_price:
        return True
    else:
        return False

# Main function
def main():
    while True:
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('localhost', 12345))
            server_socket.listen(1)
            print("Bank is listening...")
            
            conn, addr = server_socket.accept()
            with conn:
                print('Connected by', addr)
                data = conn.recv(1024).decode()
                print("Received data from client:", data)
                data_parts = data.split("||")
                if len(data_parts) == 4:  # Check if data has expected format
                    item_price, customer_name, credit_card_number, signature = data_parts
                    if verify_signature(data.encode(), signature.encode(), server_public_key):
                        if validate_transaction(customer_name, credit_card_number, int(item_price)):
                            update_creditinfo(customer_name, int(item_price), credit_card_number) # Update credit info with the price
                            response = "1"  # Success
                        else:
                            response = "0"  # Unauthorized
                    else:
                        response = "0"  # Unauthorized
                    conn.sendall(response.encode())
                else:
                    print("Received malformed data:", data)
        except Exception as e:
            print("Error occurred in bank:", e)
            traceback.print_exc()  # Print traceback for detailed error information
        finally:
            server_socket.close()


if __name__ == "__main__":
    main()
