import hashlib
import random
import string


HASH_DELIM = '|'


def make_salt():
    return ''.join(random.sample(string.ascii_letters, 16))


def encrypt(s):
    return hashlib.sha256(s).hexdigest()


def make_hash(s):
    salt = make_salt()
    h = encrypt(s + salt)
    return h + HASH_DELIM + salt


def check_against_hash(s, h):
    hashed, salt = h.split(HASH_DELIM)
    return hashed == encrypt(s + salt)