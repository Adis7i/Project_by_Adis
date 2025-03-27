import argparse
from cryptography.fernet import Fernet, InvalidToken
from pathlib import Path
import os
import json
import struct
import hashlib
import base64
import shutil
from datetime import datetime
from sys import exit
parser = argparse.ArgumentParser(description="Simple encryption with Fernet")
parser.add_argument("mode", choices= ["encrypt", "decrypt"],help="changemode to decrypt or encrypt")
parser.add_argument("path", help="enter path or name to or of a file to encrypt")
parser.add_argument("key", help="enter password to encrypt file")
parser.add_argument("--unsafe", action="store_true", help="Perform encryption without backuping the file")
parser.add_argument("--storepass", action="store_true", help="Saving your keys")

args = parser.parse_args()

class FileEncryptor() :
    def __init__(self) :
        try :
            # Necessary variable
            self.key = self.generate_key(args.key)
            self.path = self.resolve_file_path(args.path) # Original file path
            try :
                self.parent = Path(__file__).parent
            except NameError :
                print("[\033[1m\033[31m!\033[0m] __file__ Variable are not present, DON'T use jupyter notebook or python REPL")
                exit()
            #Configuration key validation
            self.config_path = self.parent / "conf.json"
            if not self.config_path.exists() :
                raise FileNotFoundError("conf.json File not founded !")
            self.config = self.getconf()
            for key in ["backup_folder", "storing_fol", "temp_file"] :
                if key not in self.config :
                    raise KeyError(f"Key {key} is missing from config !")
            if not isinstance(self.config["backup_folder"], str) :
                raise ValueError("\'backup_folder\' key is NOT a string !")
            if not isinstance(self.config["storing_fol"], dict) :
                raise ValueError("\'storing_fol\' key is NOT a dictionary !")
            if not isinstance(self.config["temp_file"], str) :
                raise ValueError("\'temp_file\' key is NOT a string !")
            for i in ["file_container", "pass_container"] :
                if i not in self.config["storing_fol"] :
                    raise KeyError(f"Key {i} is missing from \'storing_fol\'")
            key_value = [
                self.config["backup_folder"],
                self.config["storing_fol"]["file_container"],
                self.config["storing_fol"]["pass_container"],
            ]
            for val in key_value :
                if val.find(".") != -1 :
                    raise ValueError("Configuration value except temp_file must not have a dot or an extension !")
            if self.config["temp_file"].find(".") == -1 :
                raise ValueError("temp_file value don't have an extension !")
            
            self.store_file: Path = self.parent / self.config["backup_folder"] / self.config["storing_fol"]["file_container"]
            self.store_pass: Path = self.parent / self.config["backup_folder"] / self.config["storing_fol"]["pass_container"]
            self.tmp: Path = self.parent / self.config["backup_folder"] /self.config["temp_file"]
            #Variable path validation
            if not args.unsafe : shutil.move(self.path, self.store_file)
            self.file_loc = self.store_file / self.path.name if not args.unsafe else self.path # Moved file path
            print(self.file_loc)
            for paths in [self.store_file, self.store_pass, self.tmp, self.file_loc] :
                print("paths", paths)
                if not paths.exists() : raise FileNotFoundError("One or more required path not founded !, check your config")
            if args.storepass : 
                f = self.store_pass / f"Backup_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}"
                f.touch()
                with open(f, "w") as s :
                    s.write(args.key)
        except json.JSONDecodeError:
            print("[\033[1m\033[31m!\033[0m] Invalid Json Format !")
            exit()
        except ValueError as e :
            print("[\033[1m\033[31m!\033[0m]", e)
            exit()
        except KeyError as e :
            print("[\033[1m\033[31m!\033[0m]", e)
            exit()
        except FileNotFoundError as e :
            print("[\033[1m\033[31m!\033[0m]", e)
            exit()
        except NameError :
            print("[\033[1m\033[31m!\033[0m] Please define everything required, put this script inside a folder")

    def getconf(self) :
        with open(self.config_path, "r") as f :
            config = json.load(f)
            return config

    @staticmethod
    def generate_key(password: str) :
        print("[i] generating key...")
        key = hashlib.sha256(password.encode()).digest()
        return base64.urlsafe_b64encode(key[:32])
    
    @staticmethod
    def resolve_file_path(file_path) :
        path = Path(file_path).expanduser()
        resolved_path = None
        if path.is_absolute() :
            print("[i] Detected path argument as an absolute path")
            resolved_path =  path.resolve()
        if path.parent != Path(".") :
            print("[\033[1m\033[33mi\033[0m] Detected path argument as relative path, joining with cwd path")
            resolved_path = Path.cwd() / path
        else :
            print("[\033[1m\033[33mi\033[0m] Detected path argument as a File name, joining with cwd")
            resolved_path = Path.cwd() / path.name
        if resolved_path.exists() :
            print(f"[\033[1m\033[32m*\033[0m] Resolved Path {resolved_path} Exists !")
            return resolved_path
        else :
            raise FileNotFoundError(f"Resolved path {resolved_path} Doesn't exists !")

    def encrypt(self) :
        fernet = Fernet(self.key)
        chunk_size = 64 * 1024
        with open(self.file_loc, "rb") as main_dat, open(self.tmp, "wb") as temp_store:
            print("[i] Reading chunk..")
            while chunk := main_dat.read(chunk_size) :
                print(f"[i] Reading {len(chunk)} bytes")
                encrypted = fernet.encrypt(chunk)
                temp_store.write(struct.pack('>Q', len(encrypted)))
                temp_store.write(encrypted)
                temp_store.flush()
                os.fsync(temp_store.fileno())
        self.path.touch()
        os.replace(self.tmp, self.path)
        self.tmp.touch()
    
    def decrypt(self) :
        fernet = Fernet(self.key)
        with open(self.file_loc, "rb") as main_dat, open(self.tmp, "wb") as temp_store:
            print("[i] Reading chunk...")
            while size_hint := main_dat.read(8) :
                size = struct.unpack('>Q', size_hint)[0]
                read_size = main_dat.read(size)
                print(f"[i] Reading {len(read_size)} bytes")
                decrypted = fernet.decrypt(read_size)
                temp_store.write(decrypted)
                temp_store.flush()
                os.fsync(temp_store.fileno())
        self.path.touch()
        os.replace(self.tmp, self.path)
        self.tmp.touch()

if __name__ == "__main__" :
    encryptor = FileEncryptor()
#    if args.mode == "encrypt" :
#        encryptor.encrypt()
#    elif args.mode == "decrypt" :
#        encryptor.decrypt()

        