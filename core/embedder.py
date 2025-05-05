import numpy as np
from PIL import Image, UnidentifiedImageError
from math import floor
from pathlib import Path
from utils import resolve_file_path
from datetime import datetime as dt
import logging
import json
from typing import Literal
from gc import collect

log_name = f"{Path(__file__).name}_{dt.now().strftime("%d-%m-%Y_%H-%M-%S")}_log.log"

logging.basicConfig(
    filename=Path(__file__).parent / ".logs" / log_name,
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)
out_name = None

def get_config() :
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

def save(image_array: np.ndarray, mode: Literal['e','d']) :
    if Path(out_name).exists() and check_name() :
        Image.fromarray(image_array).save(out_name)
    else :
        config = get_config()
        locker = Path(__file__).parent / config["storing_folder"] / config["locker"]
        out_name = locker / config["encoded_container"] if mode == 'e' else config["decoded_container"] / Path(out_name).name
        

def get_image_array(image_path: str|Path) :
    return np.array(Image.open(str(image_path)))

def get_file_bytearray(file_path: Path) -> tuple[bytearray, int] :
    data_array = bytearray()
    file_path: bytes = file_path.read_bytes()
    data_size = len(file_path) + 4
    data_array.extend(data_size.to_bytes(4, 'little'))
    data_array.extend(file_path)
    del file_path
    return data_array, data_size

def encode(file: str|Path, image: str|Path) -> None :
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