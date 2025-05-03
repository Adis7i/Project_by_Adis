from cryptography.fernet import Fernet
from pathlib import Path
import os
import struct
from hashlib import pbkdf2_hmac, sha256
import base64
from shutil import move
from datetime import datetime as dt
from typing import Literal
import logging
from utils.common import resolve_file_path
from json import load

log_name = f"{Path(__file__).name}_{dt.now().strftime("%d-%m-%Y_%H-%M-%S")}_log.log"

logging.basicConfig(
    filename=Path(__file__).parent / "logs" / log_name,
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

class AFEncryptor() :
    """
    A class for custom encryption either message or file path\n
    modify key simply by using AFEncryptor.password, and AFEncryptor.salt\n then use AFEncryptor.var_setup() to update changes 
    """
    def __init__(self, password : str, salt : int):
        logging.info(f"Class AFEncryptor created")
        self.password = password
        self.salt = salt
        self.__key = None
        self.__allow_execute = False
        self.__config = None
        self.__parent_path = Path(__file__).parent
        self.__file_container = None
        self.__pass_container = None
        self.__tmp = None
        self.var_setup()

    @staticmethod
    def generate_key(key: str, salt : bytes) -> bytes :
        key = pbkdf2_hmac(
            'sha256', 
            password=key.encode(), 
            salt=salt, 
            iterations=100000,
            dklen=32
        )
        return base64.urlsafe_b64encode(key)
    
    def var_setup(self) -> None:
        """
        Method to checking and setting up system variables for initial processing and updating changes

        this method determine whether the core method are allowed or not
        
        in which prevent exception which causes unwanted exiting especially when putted into Command Line like Interface
        """
        logging.info("setting up variables")
        self.__allow_execute = True
        try :
            logging.info("loading up config and setting system path")
            self.__get_config()
            locker_path = self.__parent_path / self.__config["storing_folder"] / self.__config["locker"]
            self.__file_container: Path = locker_path / self.__config["file"]
            self.__pass_container: Path = locker_path / self.__config["pass"]
            self.__tmp: Path = self.__parent_path / self.__config["tmp_folder"] / self.__config["tmp"]
        except Exception as msg :
            logging.error(f"Can't load up config check your config file !\nmsg : {msg}")
            self.__allow_execute = False

        try :
            logging.info("generating key")
            self.__key = self.generate_key(self.password, self.salt.to_bytes(16, 'big'))
        except Exception as msg:
            logging.error(f"Error at generating key please check your input !\nmsg : {msg}")
            self.__allow_execute = False

        if all(i.exists() for i in [self.__file_container, self.__pass_container, self.__tmp]) :
            for i in [self.__file_container, self.__pass_container] :
                if i.is_file() :
                    logging.critical(f"Path \'{str(i)}\' does not lead to a folder !")
                    self.__allow_execute = False
            if self.__tmp.is_dir() :
                self.__allow_execute = False
                logging.critical(f"Path \'{str(self.__tmp)}\' does not lead to a file !")
        else :
            logging.warning("One or more system path does not exists !")
            self.__allow_execute = False

        if self.__allow_execute  :
            logging.info("All basic variable condition are met ! ending __setting_variable()")
        else :
            logging.warning("There is some error or non-existing path, please check your config AND input\nFurther more core processing are prohibited")
    
    def save_file(self, path) -> bool:
        """
        Method to move file, if successful returns true, if not returns False
        """
        logging.info("Moving file...")
        try :
            move(path, self.__file_container / Path(path).name)
            return True
        except Exception as msg :
            logging.error(f"Can't move the file ! msg : {msg}")
            return False

    def encrypt(self, msgorpath: str, mode: Literal['path','msg'], save: bool = True) -> None|str :
        """
        This method is the core processing of this class designed for flexibility
        """
        logging.info("begin encryption")
        if mode == "path" and self.__allow_execute:
            try :
                file_path = resolve_file_path(msgorpath)
                true_path = file_path
                if_save_condition = True
                if save :
                    if_save_condition = self.save_file(file_path)
                    true_path = self.__file_container / file_path.name
            except Exception as msg :
                logging.critical(f"Failed to resolve file path check your input !, msg : {msg}")
                if_save_condition = False

            if file_path and if_save_condition :
                fernet = Fernet(self.__key)
                SIZE = 64 * 1024
                with open(true_path, 'rb') as source, open(self.__tmp, 'wb') as temp :
                    while chunk := source.read(SIZE) :
                        chunk = fernet.encrypt(chunk)
                        temp.write(struct.pack('>Q', len(chunk)))
                        temp.write(chunk)
                        temp.flush()
                        os.fsync(temp.fileno())
                file_path.touch()
                os.replace(self.__tmp, file_path)
                self.__tmp.touch()
                logging.info("Encryption sucessful...")
            else :
                logging.warning("encryption process are prohibited")
        elif mode == 'msg' and self.__allow_execute :
            fernet = Fernet(self.__key)
            try :
                logging.info("Returning result")
                return fernet.encrypt(msgorpath.encode())
            except Exception as msg :
                logging.error(f"Encryption unsuccesful please check your input ! \nmsg : {msg}")
        else :
            logging.warning("Abort..., either core processing are prohibited or mode option are wrong")
    
    @property
    def salts(self) :
        return self.salt
    @property
    def passwords(self) :
        return self.password
    @property
    def keys(self) :
        return self.__key

    def __get_config(self) :
        with open(self.__parent_path / "general_config.json", 'r') as f :
            self.__config = load(f)["encrypt_app"]

    def cat_log(self) -> str|None:
        with open(Path(__file__).parent / "logs" / log_name, 'r') as source :
            return source.read()    

  
encryptor = AFEncryptor("my_pass", 123456)
encryptor.encrypt("QACC.py", 'path')
print(encryptor.cat_log())

