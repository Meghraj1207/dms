from hashids import Hashids

hashids = Hashids(salt="dms_secret_salt", min_length=8)

def encode_id(id):
    return hashids.encode(id)

def decode_id(hashid):
    decoded = hashids.decode(hashid)
    return decoded[0] if decoded else None