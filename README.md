# AFEncryptor (Advanced File Encryptor)

## Description
AdvancedFileEncryptor2000 is a program designed for encryption and decryption tasks. It provides both command-line and user-friendly UI modes for various cryptographic functions

## Requirements
- The **cryptography** library (version 41.*) is recommended if you're having trouble with Rust-based cryptography.
  - If you're facing issues with cryptography using Rust, download **cryptography library version 41.\*** (this is based on personal experience with the version used by my dad).

### Command-Line Mode
You can use the script `endecrypt.py` directly in the command line with the following syntax:

```bash
python3 endecrypt.py [-h] [--unsafe] [--storepass] {encrypt,decrypt} path key
```

**Arguments:** <br>
- -h: Show help message.

- --unsafe: (Optional) Enable unsafe mode.

- --storepass: (Optional) Store the password.

- {encrypt,decrypt}: Specify the action to perform, either encryption or decryption.

- path: Specify the file path for encryption/decryption.

- key: Specify the key for the encryption/decryption.
 
### User-Friendly UI Mode
for more user-friendly interface, run Console.py
```bash
python3 Console.py
```

### Important Note
- Please do not change the name of any file in this folder except the one that's in the *Backup* folder
- Please run in venv for safer option, *sys.path* are being modified to ensure there is no error at importing module from another folder

## Folder Structure
Please follow the folder structure below to ensure program to work properly *(In case you may have messed up something with it)*
```
AdvancedFileEncryptor2000/  
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

# FileSeeker

## Description
FileSeeker (*Often referred as manual mode*) is a manual file searching mode

## Features
- Positive quote (Threading)

- Quote can be deactivate

- Multipath picking

# Note
Before quitting program needs **11 seconds** to fully exit because of terminal redrawing session

# EmbedFileToImage

## Description
Embedding file to image program, can either encode or decode

# Important Note
- Every program needs it's other module such as Global_Function Module 