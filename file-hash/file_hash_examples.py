import hashlib
import hmac, os
from collections import defaultdict
from pathlib import Path

with open("backup.zip", "rb") as f:
    digest = hashlib.file_digest(f, "sha256").hexdigest()
# digest is a 64-character hex string

guaranteed = sorted(hashlib.algorithms_guaranteed)
# ['blake2b', 'blake2s', 'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha3_224',
#  'sha3_256', 'sha3_384', 'sha3_512', 'sha512', 'shake_128', 'shake_256']

def sha256_of(path):
    with open(path, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

h = sha256_of("notes.txt")
# '018369bfb9bf2f0cf3a6d669a3d55cacff4da2b10f3b28bee8ffe74d7465dcf1'

def hash_file(path, algorithm="sha256", chunk_size=1024 * 1024):
    h = hashlib.new(algorithm)
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()

same = hash_file("notes.txt") == sha256_of("notes.txt")   # True
print('same', '=', repr(same))

published = "018369BFB9BF2F0CF3A6D669A3D55CACFF4DA2B10F3B28BEE8FFE74D7465DCF1 "
ok = sha256_of("notes.txt") == published.strip().lower()   # True
print('ok', '=', repr(ok))


salt = os.urandom(16)
key = hashlib.scrypt(b"tea-time-42", salt=salt, n=2**14, r=8, p=1)
match = hmac.compare_digest(key, hashlib.scrypt(b"tea-time-42", salt=salt, n=2**14, r=8, p=1))   # True
print('match', '=', repr(match))


def find_duplicates(folder):
    by_hash = defaultdict(list)
    for path in Path(folder).rglob("*"):
        if path.is_file():
            by_hash[sha256_of(path)].append(str(path.relative_to(folder)))
    return [names for names in by_hash.values() if len(names) > 1]

dupes = find_duplicates("photos")    # [['beach-copy.jpg', 'beach.jpg']], order may vary
print('dupes', '=', repr(dupes))
