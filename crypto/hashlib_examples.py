import hashlib # hashlib module
import os.path # For file handling
from os import path
 
def hash_file(filename):
 
    if path.isfile(filename) is False:
        raise Exception("File not found for hash operation") 
 
    # make a hash object
    h_sha256 = hashlib.sha256()
 
    # open file for reading in binary mode
    with open(filename,'rb') as file:
 
        # read file in chunks and update hash
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024) 
            h_sha256.update(chunk)
 
    # return the hex digest
    return h_sha256.hexdigest()

# Prints {'shake_256', 'sha1', 'blake2s', 'sha3_224', 'sha512', 'sha3_256', 'sha224', 'sha256', 'sha3_384', 'sha384', 'blake2b', 'sha3_512', 'shake_128', 'md5'}
print(hashlib.algorithms_guaranteed)

# Getting hash of the file
message = hash_file("Python.txt")
print(message)
