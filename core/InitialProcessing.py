from pathlib import Path
import json
from sys import exit
from time import sleep
from os import access, R_OK, W_OK, X_OK
from os.path import isdir
if __name__.find(".") != -1 :
    from .EncryptorSetup import set_outer_module_importable
else :
    from EncryptorSetup import set_outer_module_importable
try :
    from utils.paintext import *
except :
    set_outer_module_importable()
    from utils.paintext import *


class InitialProcessing():
    def __init__(self) :
        """
        Checking conf.json configuration integrity,
        
        and overall check the permission and existence of
        the configuration file and folder references 
        """
        try :
            try :
                self.path = Path(__file__).parent
            except NameError :
                print(f"{CRITICAL} Don't import or run this script using python REPL")
                exit()
            self.config: dict = self.get_conf()
            self.paths = self.path_checker(self.conf_checker())
            self.rwPermissionFolder_checker(self.paths)
            sleep(2)

        except json.JSONDecodeError as m :
            print(f"{CRITICAL} conf.json Is corrupted !, message : \'{m}\'")
        except FileNotFoundError as m :
            print(f"{CRITICAL} {m} f")
            exit()
        except ValueError as m :
            print(f"{CRITICAL} {m} v")
            exit()
        except IsADirectoryError as m :
            print(f"{CRITICAL} {m} i")
            exit()
        except NotADirectoryError as m :
            print(f"{CRITICAL} {m} n")
            exit()
        except PermissionError as m :
            print(f"{CRITICAL} {m} p")
            exit()
        
    def returnpath(self) :
        return self.paths

    def get_conf(self) -> dict:
        with open(self.path / "conf.json", "r") as f:
            return json.load(f)


    def conf_checker(self) -> dict[Path, Path, Path] :
        """
        Function to check the current File structure
        """
        #Checking the required key

        required_tags = ["backup_folder","storing_fol","temp_file"]
        required_tags2 = ["file_container","pass_container"]
        for i in required_tags :
            content = self.config[i]
            if not content :
               raise ValueError(f"Key value of {i} is empty, value: {content}")
            
        if not isinstance(self.config["backup_folder"], str) :
            raise ValueError("\'backup_folder\' key is NOT a string !")
        
        if not isinstance(self.config["storing_fol"], dict) :
            raise ValueError("\'storing_fol\' key is NOT a dictionary !")
        
        if not isinstance(self.config["temp_file"], str) :
            raise ValueError("\'temp_file\' key is NOT a string !")
        
        for i in required_tags2 :
            cont = self.config["storing_fol"][i]
            if not cont or not isinstance(cont, str) :
                raise ValueError(f"Key value of {i} is empty or not a string, value: {cont}")
            
        print(f"{SUCCES} Config is not corrupted")
        temp = Path(self.path / self.config["backup_folder"] / self.config["temp_file"])
        f_con = Path(self.path / self.config["backup_folder"] / self.config["storing_fol"]["file_container"])
        p_con =  Path(self.path / self.config["backup_folder"] / self.config["storing_fol"]["pass_container"])
        if isdir(temp) :
            raise IsADirectoryError(f"{temp.name} Was not a file !")
        if not isdir(f_con) :
            raise NotADirectoryError(f"{f_con.name} Was not a folder !")
        if not isdir(p_con) :
            raise NotADirectoryError(f"{p_con.name} Was not a folder !")

        return {
            "tmp_path" : temp,
            "file_cont" : f_con,
            "pass_cont" : p_con
        }
    @staticmethod
    def path_checker(path_dic: dict[Path]) -> dict:
        for i in path_dic.keys() :
            path = path_dic[i]
            if not path.exists() :
                raise FileNotFoundError(f"Path {str(path)} doesn't exist")
            else :
                print(f"{SUCCES} Path {str(path)} exists !")
        return path_dic
    
    @staticmethod
    def rwPermissionFolder_checker(paths: dict[Path]):
        for i in paths.keys() :
            path = paths[i]
            if not (access(path, R_OK) and access(path, W_OK)) :
                raise PermissionError(f"Read or Write access to path {str(path)} is not permissible")
        return paths
    
