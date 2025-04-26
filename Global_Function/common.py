if __name__.find(".") != -1 :
    from .paintext import *
else :
    from paintext import *
from pathlib import Path
from os import path

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
    Checks multiple path, return status 1 if all 
    """
    stat = True
    for i in paths :
        if path.exists(i) :
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
