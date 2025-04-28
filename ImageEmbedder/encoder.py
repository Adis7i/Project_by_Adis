from pathlib import Path
from PIL import Image, UnidentifiedImageError
import os
import sys
import argparse
from time import sleep
from math import floor
from typing import Literal
import numpy as np
from datetime import datetime
try :
    from Global_Function import FileSeeker, resolve_file_path
    from Global_Function.paintext import *
except :
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from Global_Function import FileSeeker, resolve_file_path
    from Global_Function.paintext import *
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
parser = argparse.ArgumentParser("Embed file to image program")
parser.add_argument("mode", choices=["encode","decode"], help="Select mode between encode or decode")
parser.add_argument("target", nargs="?", type=str, help="Enter desired file path to encode, leave blank if choose decode")
parser.add_argument("image", type=str, help="Enter the desired Image path, required for both encode and decode unless if using manual mode")
parser.add_argument("name", nargs="?", type=str, help="Enter the desired file name, default name is datetime")
parser.add_argument("--manual", action="store_true", help="use this flag to enter manual file picking")
if __name__ == "__main__" : 
    args = parser.parse_args()

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
        self.target_file = target_path
        self.image_file = image_path
        self.is_manual: bool = is_manual
        self.out_name = outfile_name if outfile_name else datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.out_name = self.out_name + ".bmp" if mode == 'encode' else self.out_name
        self.mode = mode
        self.dat_array = bytearray()
        self.data_size = 0
        self.max_data_size = 0
        self.InitialProcessing()
    
    def InitialProcessing(self) :
        try :
            if self.mode not in ["encode","decode"] :
                raise ValueError("Unknown mode selected")
            if not isinstance(self.is_manual, bool) :
                raise ValueError(f"is_manual parameter must be a 'bool', Not '{type(self.is_manual).__name__}'")
            
            if self.mode == 'encode' :
                if self.is_manual :
                    seeker = FileSeeker(Path.cwd(), is_thread=False, title="Pick target file")
                    sleep(3)
                    seeker.changetitle("Pick target file")
                    self.target_file = seeker.main()
                    seeker.changetitle("Pick image file")
                    self.image_file = seeker.main()

                if not self.target_file or not self.image_file :
                    raise ValueError("One or two required file path are NOT provided")

                self.target_file = resolve_file_path(self.target_file).read_bytes()
                self.data_size = len(self.target_file) + 4
                self.dat_array.extend(self.data_size.to_bytes(4, 'little'))
                self.dat_array.extend(self.target_file)

            elif self.mode == 'decode' :
                if self.is_manual :
                    self.image_file = FileSeeker(Path.cwd(), is_thread=False, title='Pick Image File').main()

            if not self.image_file :
                raise ValueError("Required Image path are missing !")

            self.image_file = resolve_file_path(self.image_file)
            self.image_file = Image.open(str(self.image_file))
            self.image_file = np.array(self.image_file)
            if self.mode == 'encode' and self.data_size >= floor(self.image_file.shape[0] * self.image_file.shape[1] * self.image_file.shape[2] * 2 // 8) :
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
        height, width, channel = self.image_file.shape
        byte_index = 0
        shift_num = 0
        for row in range(0, height) :
            for col in range(0, width) :
                for chnl in range(0, channel) :
                    self.image_file[row, col, chnl] = self.image_file[row, col, chnl] & 0xFC | (self.dat_array[byte_index] >> (shift_num * 2))
                    shift_num += 1
                    shift_num %= 4
                    if shift_num == 0 :
                        byte_index += 1
                        if byte_index >= self.data_size  :
                            return

    def decode(self):
        height, width, channel = self.image_file.shape
        byte = 0
        byte_index = 0
        shift_num = 0
        self.data_size = 5
        for row in range(0, height):
            for col in range(0, width):
                for chnl in range(0, channel):
                    
                    byte = (byte >> 2) | (self.image_file[row, col, chnl] << 6)
                    shift_num += 1
                    shift_num %= 4
                    
                    if shift_num == 0:
                        if byte_index <= 4:
                            if byte_index == 4:
                                self.data_size= int.from_bytes(self.dat_array, byteorder='little')
                                self.dat_array = bytearray()  
                        self.dat_array.extend(byte) 
                        byte_index += 1
                        byte = 0  

                        if byte_index >= self.data_size:
                            return
    
    def main(self)  :
        if self.mode == "encode" :
            self.encode()
            img = Image.fromarray(self.image_file)  
            img.save(str(FP / IMAGESTORE / self.out_name))
        elif self.mode == "decode" :
            self.decode()
            with open(FP / DECODEDSTORE / self.out_name, 'wb') as file :
                file.write(self.dat_array)

if __name__ == "__main__" :
    Embedder = FileEmbedder(
        target_path=args.target,
        image_path=args.image,
        mode=args.mode,
        is_manual=args.manual,
        outfile_name=args.name
    )
    Embedder.main()


