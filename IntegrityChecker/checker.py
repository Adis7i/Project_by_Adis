import os
import sys
import csv
from pathlib import Path
from hashlib import sha256
from datetime import datetime as dt
try :
    from Global_Function import FileSeeker, MultPath, remlist_all
    from Global_Function.paintext import *
except :
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from Global_Function import FileSeeker, MultPath, remlist_all
    from Global_Function.paintext import *


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
                if not os.access(i, os.W_OK | os.R_OK) :
                    raise PermissionError("Either DATA_PATH or TEMP_PATH are not permissible to read and write")
            for i in paths :
                if not os.access(i, os.R_OK) :
                    raise PermissionError(f"Reading path {i} was NOT permissible")
            self.paths = paths

        except ValueError as e :
            print(f"{CRITICAL} Invalid value : {e}")
            sys.exit()
        except FileNotFoundError as e :
            print(f"{CRITICAL} Error, file not found : {e}")
            sys.exit()
        except PermissionError as e :
            print(f"{CRITICAL} Permission denied : {e}")
            sys.exit()
        except Exception as e :
            print(f"{CRITICAL} Unexpected exception was raised : {e}")
            sys.exit()
    
    @staticmethod
    def get_hash(path) -> str :
        hash_val = sha256()
        SIZE = 64 * 1024
        with open(path, 'rb') as source :
            while chunk := source.read(SIZE) :
                hash_val.update(chunk)
        return hash_val.hexdigest()
    
    
    def get_file_report(self, path: Path, hash_val, mtime, strformat) -> str :
        if not isinstance(path, Path) :
            raise ValueError(f"path Parameter must be Path from pathlib, not \'{type(path).__name__}\'")
        if not path.exists() :
            raise FileNotFoundError(f"\'path\' Parameter, path does not exist !")
        if path.is_dir() :
            raise IsADirectoryError(f"\'path\' Parameter must lead to a file, not a directory")
        
        recorded_mtime = dt.fromtimestamp(mtime).strftime(strformat)
        actual_mtime = dt.fromtimestamp(path.stat().st_mtime).strftime(strformat)

        return f"""File Path : {str(path)}
File Hash : {self.get_hash(path)} ({recorded_mtime})
File Mtime : {path.stat().st_mtime} ({actual_mtime})
Recorded Hash : {hash_val}
Recorded Mtime : {mtime}"""
        
    def main(self) -> None :
        KEYS = ['path','hash','mtime']
        strformat = "%Y-%m-%d_%H:%M:%S"
        with open(DATA_PATH, 'r') as source, open(TEMP_PATH, 'w') as temp, open(LOG_PATH, 'a') as logger :
            logger.write(f"=====START OF REPORT=====\n")
            logger.write(f"[{dt.now().strftime(strformat)}] Start file opening\n")
            reader = csv.DictReader(source)
            writer = csv.DictWriter(temp, fieldnames=reader.fieldnames)
            writer.writeheader()
            should_write = True
            for i in KEYS :
                if i not in reader.fieldnames :
                    logger.write(f"[{dt.now().strftime(strformat)}] Raised exception because of Missing Fieldnames\n")
                    raise FieldnameError(f"Missing required fieldname {i}")
            logger.write(f"[{dt.now().strftime(strformat)}] Starting scanning phase\n")
            for indx, row in enumerate(reader) :
                should_write = True
                logger.write(f"[{indx}] Iteration : scanning file\n")
                path = Path(row['path'])
                hash_val = row['hash']
                modtime = row['mtime']
                if not path.exists() :
                    print(f"{UNREC} Path {path} Doesn't exist !")
                    should_write = False
                    logger.write(f"[{indx}] Iteration : WARNING \'{path}\' Doesn't exists !\n")
                    continue

                file_hash = self.get_hash(path)
                if hash_val != file_hash :
                    print(f"{CRITICAL} Path \'{path}\' Compromised !")
                    logger.write(f"[{indx}] Iteration : {path.name} INTEGRITY COMPROMISED\n")
                    logger.write(f"[{dt.now().strftime(strformat)}] ===On time, Report===\n{self.get_file_report(path, hash_val, modtime, strformat)}\n")
                    logger.write(f"[{indx}] ===Generating new hash===\n")
                    row['hash'] = self.get_hash(path)
                    row['mtime'] = path.stat().st_mtime

                self.paths = remlist_all(path, self.paths)
                if should_write :
                    writer.writerow(row)
            
            if self.paths :
                logger.write(f"[{dt.now().strftime(strformat)}] Assigning new file\n")
                for i in self.paths :
                    if os.path.exists(i) :
                        logger.write(f"Path {i} Exists writing down file information\n")
                        writer.writerow({'path' : i, 'hash' : self.get_hash(i), 'mtime' : Path(i).stat().st_mtime})
            logger.write(f"=====END OF REPORT=====\n\n")
        os.replace(TEMP_PATH, DATA_PATH)
        Path(TEMP_PATH).touch()


#This is not ready yet