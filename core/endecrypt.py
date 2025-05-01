from cryptography.fernet import Fernet, InvalidToken
from pathlib import Path
import os
import struct
from hashlib import pbkdf2_hmac
import base64
from shutil import move, Error
from datetime import datetime
from sys import exit
from typing import Literal
import logging
if __name__.find(".") != -1 :
    from .InitialProcessing import InitialProcessing
else :
    from InitialProcessing import InitialProcessing
try :
    from utils.paintext import *
    from utils import resolve_file_path
except ModuleNotFoundError :
    from utils.paintext import *
    from utils import resolve_file_path

class EncryptorError(Exception) :
    def __init__(self, m):
        super().__init__(m)

class FileEncryptor() :
    def __init__(
            self, 
            path: str|Path, 
            key: str, 
            mode: Literal["encrypt","decrypt"], 
            salt: str, 
            option_pass=False, 
            option_safe=False
        ) :
        """
        A simple encryption class, main() to execute
        """
        init = InitialProcessing() #Checks overall paths and variable required to run this script
        self.salt = int(salt).to_bytes(16, 'big') if salt.strip().isdecimal() else os.urandom(16)
        self.paths = init.returnpath()
        self.tmp: Path = self.paths["tmp_path"]
        self.f_con: Path = self.paths["file_cont"]
        self.p_con: Path = self.paths["pass_cont"]
        self.mode = mode

        try :
            self.key, self.salt = self.generate_fernet_key(key, self.salt)
            print("[i] Salt and key generated")
            self.source_path = resolve_file_path(path)
            self.file_path = self.source_path

            if isinstance(self.salt, bytes) and mode == "decrypt" :
                raise EncryptorError("Decrypting file with a random salt is not possible !")
            
            if option_safe : 
                move(self.source_path, self.f_con)
                self.file_path = self.f_con / self.source_path.name
                print(f"[i] File moved from {str(self.source_path.parent)} to {str(self.file_path.parent)}")

            if option_pass :
                pass_backup_file = self.p_con / f"{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}"
                pass_backup_file.touch()
                with open(pass_backup_file, 'w') as file :
                    file.write(f"Key : {key}\nSalt  : {self.salt}")
                print("[i] Pass and salt backup created")
            else :
                print(f"{UNREC} Password and salt backup are not created, Just in case\nSalt -> {self.salt}")

        except OverflowError :
            print(f"{CRITICAL} Please enter a salt that was an integer beetwen 0 to 340.28 undecillion !")
        except EncryptorError as e :
            print(f"{CRITICAL} {e}")
            exit()
        except FileNotFoundError as e :
            print(f"{CRITICAL} {e}")
            exit()
        except Error as e :
            print(f"{CRITICAL} {e}")
            exit()
        

    @staticmethod
    def generate_fernet_key(password: str, salt: bytes) :
        """
        Generate 32-byte url-safe base64 encoded strings
         
        fulfilling fernet encryption key requirements
        """

        key = pbkdf2_hmac('sha256', password.encode(), salt, 100000, dklen=32)
        return base64.urlsafe_b64encode(key), int.from_bytes(salt, 'big')


    def encrypt(self) :
        fernet = Fernet(self.key)
        chunk_size = 64 * 1024
        with open(self.file_path, "rb") as main_dat, open(self.tmp, "wb") as temp_store:
            print("[i] Reading chunk..")
            while chunk := main_dat.read(chunk_size) :
                print(f"[i] Reading {len(chunk)} bytes")
                encrypted = fernet.encrypt(chunk)
                temp_store.write(struct.pack('>Q', len(encrypted)))
                temp_store.write(encrypted)
                temp_store.flush()
                os.fsync(temp_store.fileno())
        self.source_path.touch()
        os.replace(self.tmp, self.source_path)
        self.tmp.touch()
    
    def decrypt(self) :
        fernet = Fernet(self.key)
        with open(self.file_path, "rb") as main_dat, open(self.tmp, "wb") as temp_store:
            print("[i] Reading chunk...")
            while size_hint := main_dat.read(8) :
                size = struct.unpack('>Q', size_hint)[0]
                read_size = main_dat.read(size)
                print(f"[i] Reading {len(read_size)} bytes")
                decrypted = fernet.decrypt(read_size)
                temp_store.write(decrypted)
                temp_store.flush()
                os.fsync(temp_store.fileno())
        self.source_path.touch()
        os.replace(self.tmp, self.source_path)
        self.tmp.touch()
    
    def main(self) :
        """
        Run the encrypting script with the desired input
        """
        if self.mode == "encrypt" :
            self.encrypt()
            print(f"{SUCCES} Encryption successful !")
        elif self.mode == "decrypt" :
            try :
                self.decrypt()
                print(f"{SUCCES} Decryption successful !")
            except MemoryError :
                print(f"{CRITICAL} File format is incorrect, decryption only works if file encrypted with the same program")
            except InvalidToken :
                print(f"{CRITICAL} File format is incorrect, decryption only works if file encrypted with the same program")        