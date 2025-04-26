import sys
from os import path 

def set_outer_module_importable() :
    """
    Adding the absolute path of this folder parent to sys.path list
    so the script in this folder can import other dependencies outside this folder
    """
    sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))
