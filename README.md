# AFEncryptor (Advanced File Encryptor)

## Description

AFEncryptor is a program designed for encryption and decryption tasks. It provides both command-line and user-friendly UI modes for various cryptographic functions

## Requirements

- The **cryptography** library (version 41.\*) is recommended if you're having trouble with Rust-based cryptography.
- If you're facing issues with cryptography using Rust, download **cryptography library version 41.\*** (this is based on personal experience with the version used by my dad).

### Command-Line Mode

You can use the script `endecrypt.py` directly in the command line with the following syntax:

```bash
python3 endecrypt.py [-h] [--unsafe] [--storepass] {encrypt,decrypt} path key salt
```

**Arguments:** <br>

- -h: Show help message.

- --unsafe: (Optional) Enable unsafe mode.

- --storepass: (Optional) Store the password.

- {encrypt,decrypt}: Specify the action to perform, either encryption or decryption.

- path: Specify the file path for encryption/decryption.

- key: Specify the key for the encryption/decryption.

- salt: Specify a random integer from 0 - 340.28 undecillion

### User-Friendly UI Mode

for more user-friendly interface, run Console.py

```bash
python3 Console.py
```

### Important Note

- Please do not change the name of any file in this folder except the one that's in the _Backup_ folder
- Please run in venv for safer option, _sys.path_ are being modified to ensure there is no error at importing module from another folder

## Folder Structure

Please follow the folder structure below to ensure program to work properly _(In case you may have messed up something with it)_

```
AFEncryptor/
├── Backup/
│   ├── content/            # Folder for moving file creating a backup
│   ├── password/           # Folder for creating password backup
│   └── tmp.bin             # Temporary Binary File
├── conf.json               # File & Folder references configuration
├── Console.py              # UI Script
├── endecrypt.py            # Encryption/Decryption Script
├── InitialProcessing.py    # Validates conf.json and checks existence of required files/folders
├── __init__.py
└── sets.py                 # Add absolute path of parent of this folder into sys.path
```

# FileSeeker (Global_Function)

## Description

FileSeeker is a file path picking program (_often referred as manual mode_),
returns a path with instance of Path from pathlib or a
list of string

## Requirements

**Built-in python library** :

- prompt_toolkit
- Threading
- Path
- os
- random
- time

## Usage

```python
path = "path/to/your/desired/directory"
seeker = FileSeeker(path, is_thread=False, title='', multipath=True)
result_path = seeker.main()
# is_thread enables positive quote
# multipath to return list of path in shape of string
```

## Note
Before quitting program needs **11 seconds** to fully exit because of terminal redrawing session

# EmbedFileToImage

## Description
Embedding file to image program, can either encode or decode

## Usage

```bash
python3 encoder.py [-h] [--manual] {encode,decode} [target] image [name]
```
## Arguments :

- -h : Show help message

- --manual : Enter manual mode file picking

- encode/decode : Mode selecting

- target : Enter file path to encode to an Image, you can **leave blank if selected decode**

- image : Enter file image path to encode or decode, **Must NOT leave blank**

- name : Optional, if leave blank. datetime is used for output file name

- **Note** : For more user-friendly mode use --manual

## Requirements
- pillow version 10.2.0

## Features

- Manual mode

- Encoding / Decoding mode

- Custom name

- Manual Mode
