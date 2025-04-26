import os
import sys
import csv
from pathlib import Path
from hashlib import sha256
from datetime import datetime as dt
try :
    from Global_Function import FileSeeker, MultPath, remlist_all
    from Global_Function.paintext import *
    from AdvancedFileEncryptor2000.endecrypt import FileEncryptor
except :
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from Global_Function import FileSeeker, MultPath, remlist_all
    from Global_Function.paintext import *
    from AdvancedFileEncryptor2000.endecrypt import FileEncryptor

#=========== PATH ===========
DATA_PATH = Path(__file__).parent / "data.csv"
TEMP_PATH = Path(__file__).parent / "tmp.csv"
LOG_PATH = Path(__file__).parent / "log.txt"
#=========== PATH ===========

class FieldnameError(Exception) :
    def __init__(self, *args):
        """
        Base class for csv fieldname exception
        """
        super().__init__(*args)

class FileChecker() :
    def __init__(self, paths: list[Path]):
        try :

            if not isinstance(paths, list) :
                raise ValueError(f"\'paths\' parameter must be list, not \'{type(paths).__name__}\'")
            if MultPath(paths + [DATA_PATH, TEMP_PATH]) :
                print(f"{SUCCES} All path exists !")
            else : 
                raise FileNotFoundError("One or more required file path is missing, may include DATA_PATH, and TEMP_PATH")
            for indx, i in enumerate(paths) :
                paths[indx] = str(i)
            for i in [DATA_PATH, TEMP_PATH] :
                if not os.access(i, os.R_OK, os.W_OK) :
                    raise PermissionError("Either DATA_PATH or TEMP_PATH are not permissible to read and write")
            for i in paths :
                if not os.access(i, os.R_OK) :
                    raise PermissionError(f"Reading path {i} was NOT permissible")
            self.paths = paths

        except ValueError as e :
            print(f"{CRITICAL} Invalid value : {e}")
        except FileNotFoundError as e :
            print(f"{CRITICAL} Error, file not found : {e}")
        except PermissionError as e :
            print(f"{CRITICAL} Permission denied : {e}")
        except Exception as e :
            print(f"{CRITICAL} Unexpected exception was raised : {e}")
    
    @staticmethod
    def get_hash(path) -> str :
        hash_val = sha256()
        SIZE = 64 * 1024
        with open(path, 'rb') as source :
            while chunk := source.read(SIZE) :
                hash_val.update(chunk)
        return hash_val.hexdigest()


    def main(self) -> None :
        KEYS = ['path','hash']
        strformat = "%Y-%m-%d_%H:%M:%S"
        with open(DATA_PATH, 'r') as source, open(TEMP_PATH, 'w') as temp, open(LOG_PATH, 'a') as logger :
            logger.write(f"[{dt.now().strftime(strformat)}] Start file opening")
            reader = csv.DictReader(source)
            writer = csv.DictWriter(temp, fieldnames=reader.fieldnames)
            writer.writeheader()
            should_write = True
            for i in KEYS :
                if i not in reader.fieldnames :
                    logger.write(f"[{dt.now().strftime(strformat)}] Raised exception because of Missing Fieldnames")
                    raise FieldnameError(f"Missing required fieldname {i}")
            logger.write(f"[{dt.now().strftime(strformat)}] Starting scanning phase")
            for row in reader :
                should_write = True
                if not os.path.exists(row['path']) :
                    print(f"{UNREC} Path {row['path']} Doesn't exist !")
                    should_write = False
                    continue
                file_hash = self.get_hash(row['path'])
                if row['hash'] != file_hash :
                    print(f"{CRITICAL} Path \'{row['path']}\' Compromised !")

                self.paths = remlist_all(row['path'], self.paths)
                if should_write :
                    writer.writerow(row)
#This is not ready yet