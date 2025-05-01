if __name__.find(".") != -1 :
    from .paintext import *
else :
    from paintext import *
from pathlib import Path
import os
from contextlib import contextmanager
from shutil import copy2, copyfileobj, rmtree
import time
def resolve_file_path(file_path: str | Path) -> Path | None :
    """
    Resolving file path by concatenating cwd with argument input if :

    Path is a filename, Or a relative path (not absolute path)

    Raise an exception if path doesn't exists
    """
    path = Path(file_path).expanduser()
    resolved_path = None
    if path.is_absolute() :
        print("[i] Detected path argument as an absolute path")
        resolved_path =  path.resolve()
    elif path.parent != Path(".") :
        print(f"{UNREC} Detected path argument as relative path, joining with cwd path")
        resolved_path = Path.cwd() / path
    else :
        print(f"{UNREC} Detected path argument as a File name, joining with cwd")
        resolved_path = Path.cwd() / path.name

    if resolved_path.exists() :
        print(f"{SUCCES} Resolved Path {resolved_path} Exists !")
        if resolved_path.is_dir() :
            raise IsADirectoryError(f"Resolved Path {resolved_path} is a directory !, required file path")
        else :
            return resolved_path
    else :
        raise FileNotFoundError(f"Resolved path {resolved_path} Doesn't exists !")

def MultPath(paths: list | tuple) -> bool :
    """
    Checks the existence of multiple path, return True if exists, False if not exists
    """
    stat = True
    for i in paths :
        if os.path.exists(i) :
            print(f"{SUCCES} Path {i} exists")
        else :
            print(f"{CRITICAL} Path {i} doesn't exists")
            stat = False
    return stat

def remlist_all(element, input_list: list) -> list | None :
    if not isinstance(input_list, list) :
        raise ValueError(f"input_list parameter must be list, not \'{type(input_list).__name__}\'")
    while element in input_list :
        input_list.remove(element)
    return input_list


class Stater() :
    def __init__(self, parent_path) :
        self.parent_path = Path(parent_path).expanduser()
        self.__backup_path = Path(__file__).parent / ".backup"
        self.__backup_path.mkdir(exist_ok=True)
        self.__saved_state = []
        self.__is_destructed = False
        self.restore_ext = False
        if not self.parent_path.exists() :
            raise FileNotFoundError(f"Path \'{str(self.parent_path)}\' does NOT exists")
        if self.parent_path.is_file() :
            raise NotADirectoryError(f"Path \'{str(self.parent_path)}\' does not lead to a FOLDER path")

    @property
    def saved_state(self) -> list :
        return self.__saved_state
    
    @property
    def is_destructed(self) -> bool :
        """
        returns True if destructed
        returns False if not destructed
        """
        return self.__is_destructed

    def save(self, filename: str) -> None :
        """
        Save a specified file from the parent folder path
        """
        if filename not in self.__saved_state and not self.__is_destructed :
            file_path = self.parent_path / filename            
            copy2(file_path, self.__backup_path)
            self.__saved_state.append(filename)
    
    def restore_all(self) :
        """
        Restore all saved file
        """
        if not self.__is_destructed :
            for filename in self.__saved_state :
                with open(self.__backup_path / filename, 'rb') as source, open(self.parent_path / filename, 'wb') as destination :
                    copyfileobj(source, destination)
    
    def restore(self, filename) -> None :
        if filename in self.__saved_state :
            with open(self.__backup_path / filename, 'rb') as source, open(self.parent_path / filename, 'wb') as destination :
                copyfileobj(source, destination)

    def destruct(self) :
        """
        Destruct the .backup folder with the item inside it
        """
        rmtree(str(self.__backup_path))
        self.__is_destructed = True
    
    def reconstruct(self) :
        """
        Reconstruct the .backup folder again
        """
        if self.__is_destructed :
            self.__backup_path.mkdir(exist_ok=True)
            self.__is_destructed = False

@contextmanager
def stating(folder_path) :
    obj_stater = Stater(folder_path)
    obj_stater.restore_ext = True
    try :
        yield obj_stater
    finally :
        if not obj_stater.is_destructed :
            obj_stater.destruct()
