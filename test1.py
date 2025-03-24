from cryptography.fernet import Fernet, InvalidToken
import hashlib
import base64
import os
import argparse
cwd = os.getcwd()

def generate_key(password: str) :
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key[:32])

def encrypt_file(filename, key)  :
    key = generate_key(key)
    fernet = Fernet(key)

    with open(filename, "rb") as file :
        data = file.read()

    encrypted = fernet.encrypt(data)

    with open(filename, "wb") as f :
        f.write(encrypted)

def decrypt_file(filename, key) :
    key = generate_key(key)
    fernet = Fernet(key)

    with open(filename, "rb") as file :
        data = file.read()

    encrypted = fernet.decrypt(data)

    with open(filename, "wb") as f :
        f.write(encrypted)

parser = argparse.ArgumentParser(description="Simple python program to encrypt no big files")

parser.add_argument("mode", choices=["encrypt", "decrypt"])
parser.add_argument("filename")
parser.add_argument("password")

args = parser.parse_args()
try :
    if args.mode == "encrypt" :
        encrypt_file(cwd + f"/{args.filename}", f"{args.password}")
    elif args.mode == "decrypt" :
        decrypt_file(cwd + f"/{args.filename}", f"{args.password}")
except InvalidToken :
    print("Error: Can't continue process, something is corrupted")
except FileNotFoundError :
    print("Error: can't continue process, File is not founded")