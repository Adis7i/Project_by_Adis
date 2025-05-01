from pathlib import Path
from PIL import Image, UnidentifiedImageError
import sys
from time import sleep
from math import floor
from typing import Literal
import numpy as np
from datetime import datetime
from utils import FileSeeker, resolve_file_path
from utils.paintext import *

IMAGESTORE = 'encoded'
DECODEDSTORE = 'decoded'
FP = Path(__file__).parent #File path
"""
This script is used for embedding file inside an Image,
The code inherets Idea from 'Engineer it Yourself' a.k.a SaadOjo in github
Author : @Adis
Credits(Github) : @SaadOjo
Date : 20-April-2025
"""

class FileEmbedder() :
    def __init__(
        self,
        target_path: str | Path,
        image_path: str | Path,
        outfile_name,
        mode: Literal["encode", "decode"],
        is_manual: bool,
    ):
        #These 2 temporarily became a path, just for checking later in will became arrays of byte
        self.__target_file = target_path
        self.__image_file = image_path
        self.__is_manual: bool = is_manual
        self.__out_name = outfile_name if outfile_name else datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.__out_name += ".bmp" if mode == 'encode' else self.__out_name
        self.__mode = mode
        self.__dat_array = bytearray()
        self.__data_size = 0
        self.InitialProcessing()
    
    def InitialProcessing(self) :
        try :
            if self.__mode not in ["encode","decode"] :
                raise ValueError("Unknown mode selected")
            if not isinstance(self.__is_manual, bool) :
                raise ValueError(f"is_manual parameter must be a 'bool', Not '{type(self.is_manual).__name__}'")
            
            if self.__mode == 'encode' :
                if self.__is_manual :
                    seeker = FileSeeker(Path.cwd(), is_thread=False, title="Pick target file")
                    sleep(3)
                    self.__target_file = seeker.main()
                    seeker.title = "Pick image file"
                    self.__image_file = seeker.main()

                if not self.__target_file or not self.image_file :
                    raise ValueError("One or two required file path are NOT provided")

                self.__target_file = resolve_file_path(self.__target_file).read_bytes()
                self.__data_size = len(self.__target_file) + 4
                self.__dat_array.extend(self.__data_size.to_bytes(4, 'little'))
                self.__dat_array.extend(self.__target_file)

            elif self.__mode == 'decode' :
                if self.__is_manual :
                    self.__image_file = FileSeeker(Path.cwd(), is_thread=False, title='Pick Image File').main()

            if not self.__image_file :
                raise ValueError("Required Image path are missing !")

            self.__image_file = resolve_file_path(self.__image_file)
            self.__image_file = Image.open(str(self.__image_file))
            self.__image_file = np.array(self.__image_file)
            if self.__mode == 'encode' and self.__data_size >= floor(self.__image_file.shape[0] * self.__image_file.shape[1] * self.__image_file.shape[2] * 2 // 8) :
                raise ValueError("Target file size exceed the permitted data size")

        except ValueError as e :
            print(f"{CRITICAL} Invalid value : {e}")
            sys.exit(1)

        except FileNotFoundError as e :
            print(f"{CRITICAL} File path not found : {e}")
            sys.exit(1)

        except IsADirectoryError as e :
            print(f"{CRITICAL} Path Error : {e}")
            sys.exit(1)

        except PermissionError as e :
            print(f"{CRITICAL} Not Permitted file access : {e}")
            sys.exit(1)

        except OSError as e :
            print(f"{CRITICAL} Failed to read file : {e}")
            sys.exit(1)

        except MemoryError as e :
            print(f"{CRITICAL} Memory Error : {e}")
            sys.exit(1)

        except UnidentifiedImageError as e :
            print(f"{CRITICAL} Error at opening Image : {e}")
            sys.exit(1)

        except Exception as e :
            print(f"{CRITICAL} Unexpected error at inital processing phase : {e}")
            sys.exit(1)

    def encode(self) :
        height, width, channel = self.__image_file.shape
        byte_index = 0
        shift_num = 0
        for row in range(0, height) :
            for col in range(0, width) :
                for chnl in range(0, channel) :
                    self.__image_file[row, col, chnl] = self.__image_file[row, col, chnl] & 0xFC | (self.__dat_array[byte_index] >> (shift_num * 2))
                    shift_num += 1
                    shift_num %= 4
                    if shift_num == 0 :
                        byte_index += 1
                        if byte_index >= self.__data_size  :
                            return

    def decode(self):
        height, width, channel = self.__image_file.shape
        byte = 0
        byte_index = 0
        shift_num = 0
        self.__data_size = 5
        for row in range(0, height):
            for col in range(0, width):
                for chnl in range(0, channel):
                    
                    byte = (byte >> 2) | (self.__image_file[row, col, chnl] << 6)
                    shift_num += 1
                    shift_num %= 4
                    
                    if shift_num == 0:
                        if byte_index <= 4:
                            if byte_index == 4:
                                self.__data_size= int.from_bytes(self.__dat_array, byteorder='little')
                                self.__dat_array = bytearray()  
                        self.__dat_array.extend(byte) 
                        byte_index += 1
                        byte = 0  

                        if byte_index >= self.__data_size:
                            return
    
    def main(self)  :
        if self.__mode == "encode" :
            self.encode()
            img = Image.fromarray(self.__image_file)  
            img.save(str(FP / IMAGESTORE / self.__out_name))
        elif self.__mode == "decode" :
            self.decode()
            with open(FP / DECODEDSTORE / self.__out_name, 'wb') as file :
                file.write(self.dat_array)
