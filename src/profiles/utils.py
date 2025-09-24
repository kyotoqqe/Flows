from typing import BinaryIO
import hashlib

def get_checksum(file: BinaryIO):
    checksum = hashlib.sha256()

    chunk = file.read(8192)
    checksum.update(chunk)
    while chunk:
        chunk = file.read(8192)
        checksum.update(chunk)
    
    return checksum.hexdigest()