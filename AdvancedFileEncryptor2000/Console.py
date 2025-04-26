from pathlib import Path
from os import system, name
from sys import exit
from typing import Literal
import tracemalloc
if __name__.find(".") != -1 :
    from .EncryptorSetup import set_outer_module_importable
    from .endecrypt import FileEncryptor
else :
    from EncryptorSetup import set_outer_module_importable
    from endecrypt import FileEncryptor
try :
    from Global_Function import FileSeeker
except ModuleNotFoundError :
    set_outer_module_importable()
    from Global_Function import FileSeeker

def console_header() :
    while True :
        system("cls" if name == "nt" else "clear")
        report = "=====Report====="
        print("=========Encryption Program=========")
        path = None
        store_file = False
        store_pass = False
        manual = False
        process_choice = int(input("\tSelect Mode:\n\t1. Encryption\n\t2. Decryption\n\tChoose (1-2) "))
        if process_choice < 1 or process_choice > 2 : 
            print("Select the proper option !")
            exit()
        if process_choice == 1 :
            process_choice = "encrypt"
            report += "\n[i] Selected Mode: Encryption"
        elif process_choice == 2 :
            process_choice = "decrypt"
            report += "\n[i] Selected Mode: Decryption"

        backup = input("\n\tBackup file? (y/n): ")
        cpassword = input("\tStore password? (y/n): ")
        manually = input("\tManual file select? (y/n): ")
        password = input("\tYour password: ")
        salt = input("\tSalt (0–340.28 undecillion or leave blank for random): ")

        if backup.strip() == 'y' :
            store_file = True
            report += "\n[i] Backup Creation: True"
        else :
            report += "\n[i] Backup Creation: False"

        if cpassword.strip() == 'y' :
            store_pass = True
            report += "\n[i] Store Password: True"
        else :
            report += "\n[i] Store Password: False"

        if manually.strip() == 'y' :
            manual = True
            report += "\n[i] Manual File Selection: True"
        else :
            report += "\n[i] Manual File Selection: False"

        report += f"\n[i] Entered Password: {password}"
        if not manual :
            path = input("Enter file path or name (can be relative path) : ")
        if process_choice == "encrypt" :
            report += "\nEnable 'Store Password' option to avoid losing the salt when encrypting files."
        
        is_sure = input(report+"\nConfirm (y/n) ")
        if is_sure == 'y' :
            break
    return (
        path, salt, password, process_choice,
        store_file, store_pass, manual
    )
    
def console_process(
        path: str,
        salt: str,
        password: str,
        mode: Literal["encrypt", "decrypt"],
        is_backup_file: bool,
        is_backup_pass: bool,
        is_manual: bool
    ) :
    if is_manual :
        path = FileSeeker(Path.cwd()).main()
    
    if path :
        encryptor = FileEncryptor(
            path=path,
            key=password,
            mode=mode,
            salt=salt,
            option_pass=is_backup_pass,
            option_safe=is_backup_file,
        )
        encryptor.main()
    else :
        print("[i] No path detected exiting...")
        exit()

def Console() :
    path, salt, key, choice, file, password, man = console_header()
    console_process(
        path=path,
        salt=salt,
        password=key,
        mode=choice,
        is_backup_file=file,
        is_backup_pass=password,
        is_manual=man
    )


if __name__ == "__main__" :
    tracemalloc.start()
    Console()
    p = tracemalloc.get_traced_memory()
    print(f"[i] Peak memory usage : {p[1]} Bytes")
    tracemalloc.stop()
    


    


