"""
This is a module for file to image embedding,

further more this program inherit logic from @SaadOjo (on github) a.k.a engineer it by yourself
on youtube

author : @Adis
credits : @SaadOjo

"""
import numpy as np
from PIL import Image
from pathlib import Path
from utils import resolve_file_path
from datetime import datetime as dt
import logging
import json
from gc import collect

LOG_NAME = f"{Path(__file__).name}_{dt.now().strftime("%d-%m-%Y_%H-%M-%S")}_log.log"
"""
str: Name of a log file use by the module to store log info, PLEASE DO NOT CHANGE THIS
"""

out_name: str = None
"""
str: Name of a path, used for image or file saving

if left non-existence path or name will be saved internally in the folder .data_storage/embedder
"""

logging.basicConfig(
    filename=Path(__file__).parent / ".logs" / LOG_NAME,
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

def _get_config() :
    with open(Path(__file__).parent / "general_config.json", 'r') as f :
        config = json.load(f)["encoder_app"]
        return config

def check_name() -> None :
    """
    Method to determine wether the out name is valid or not
    """
    if isinstance(out_name, str) and out_name :
        return True
    else :
        return False
        
def image_save(image_array : np.ndarray) :
    """
    Save image using out_name, 
    """
    global out_name
    logging.info("Saving image")
    try :
        if check_name() :
            out_path = Path(out_name)
            if out_path.parent.exists() :
                logging.warning("Warning if a same file exists in the saving directory this will threw an error")
                img = Image.fromarray(image_array)
                img.save(str(out_path))
            else :
                logging.warning("Warning if a same file exists in the saving directory this will threw an error")
                config = _get_config()
                locker = Path(__file__).parent / config["storing_folder"] / config["locker"]
                out_name = locker / config["encoded_container"] / out_path.name
        else :
            logging.warning("out_name is not valid !")
    except Exception as msg:
        logging.error(f"Error while saving image \nmsg: {msg}")

def file_save(file_array : bytearray) :
    """
    Save file data from bytearray with out_name, 
    """
    global out_name
    logging.info("Saving file")
    try :
        if check_name() :
            out_path = Path(out_name)
            if out_path.parent.exists() :
                logging.warning("Warning if a same file exists in internal saving directory this will threq an error")
                out_path.touch()
                with open(out_path, 'wb') as f :
                    f.write(file_array)
                logging.info("saving complete !")
            else :
                config = _get_config()
                locker = Path(__file__).parent / config["storing_folder"] / config["locker"]
                out_name = locker / config["encoded_container"] / out_path.name
                logging.info("saving complete !")
        else :
            logging.warning("out_name is not valid !")
    except Exception as msg:
        logging.error(f"Error while saving file \nmsg: {msg}")

def cat_log() :
    with open(Path(__file__).parent / ".logs" / LOG_NAME, 'r') as f :
        return f.read()

def get_image_array(image_path: str|Path) :
    logging.info("Getting image array")
    return np.array(Image.open(str(image_path)))

def get_file_bytearray(file_path: Path) -> tuple[bytearray, int] :
    logging.info("Getting file array")
    data_array = bytearray()
    file_path: bytes = file_path.read_bytes()
    data_size = len(file_path) + 6
    data_array.extend(b"@#")
    data_array.extend(data_size.to_bytes(4, 'little'))
    data_array.extend(file_path)
    del file_path
    return data_array, data_size

def encode(file: str|Path, image: str|Path) -> np.ndarray:
    logging.info("Starting encoding process")
    allow_execute = True
    try :
        logging.info("getting file and image data array")
        file, file_size = get_file_bytearray(resolve_file_path(file))
        image: np.ndarray = get_image_array(resolve_file_path(image))
        height, width, channel = image.shape
        if file_size > ((height * width * channel) / 4) :
            allow_execute = False
            logging.warning("target file is too big...")
    except Exception as msg :
        logging.error(f"Fail to resolve file path or getting data array, check your input !\nmsg : {msg}")
        allow_execute = False
    
    if allow_execute and check_name() :
        try :
            logging.info("All things are checked starting core process")
            shift_num = 0
            byte_index = 0
            for row in range(0, height) :
                for col in range(0, width) :
                    for chnl in range(0, channel) :
                        image[row, col, chnl] = image[row, col, chnl] & 0xFC | (file[byte_index] >> (shift_num * 2) & 0x3)
                        shift_num += 1
                        shift_num %= 4
                        if shift_num == 0 :
                            byte_index += 1
                            if byte_index >= file_size :
                                del file
                                collect()
                                return image

        except Exception as msg :
            logging.error(f"Something went wrong\nmsg : {msg}")
    else :
        logging.warning("Core process are prohibited check your input !")

def decode(image: str|Path) -> bytearray|None :
    logging.info("Start decoding process") 
    allow_execute = True
    try :
        image: np.ndarray = get_image_array(resolve_file_path(image))
        data_array = bytearray()
    except Exception as msg:
        allow_execute = False
        logging.error(f"Failed on resolving file path or getting image array !\nmsg:{msg}")
    
    if allow_execute :
        logging.info("All requirements checked starting core process")
        height, width, channel = image.shape
        byte_indx = 0
        shift_num = 0
        byte = 0
        limit = 7
        for row in range(0, height) :
            for col in range(0, width) :
                for chnl in range(0, channel) :
                    byte = (byte >> 2) | (image[row, col, chnl] << 6)
                    shift_num += 1
                    shift_num %= 4
                    if shift_num == 0 :
                        byte_indx += 1
                        data_array.extend(byte)
                        if byte_indx >= limit :
                            logging.info("Decoding finished...")
                            return data_array
                        if byte_indx <= 6 :
                            if byte_indx == 2:
                                if not data_array.startswith(b"@#"):
                                    logging.warning("Invalid image !")
                                    break
                                else :
                                    logging.info("Image file is valid !")
                                    data_array = bytearray()
                            if byte_indx == 6 :
                                limit = int.from_bytes(data_array, 'little')
                                logging.info(f"Detected file size around {limit-6} bytes")
                                data_array = bytearray()


