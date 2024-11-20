import os
import rsa
"""
## for creating private keys
pub_key, priv_key = rsa.newkeys(1024)

with open("public.pem", 'wb') as f:
    f.write(pub_key.save_pkcs1("PEM"))
with open("private.pem", 'wb') as f:
    f.write(pub_key.save_pkcs1("PEM"))



### sample code simple for reading keys 
with open("public.pem", 'rb') as f:
    pub_key = rsa.PublicKey.load_pkcs1(f.read())
with open("private.pem", 'rb') as f:
    priv_key = rsa.PrivateKey.load_pkcs1(f.read())
    
msg = "12345"

enc_mg = rsa.encrypt(msg.encode(encoding="utf-8"), pub_key)
print(enc_mg)

unc = rsa.decrypt(enc_mg, priv_key).decode(encoding="utf-8")
print(unc)
"""
# Define the maximum message length (original was 1024)
MAX_RSA_KEY_SIZE_BYTES = 1024 // 8  # 128 bytes
PADDING_OVERHEAD = 11  # PKCS#1 v1.5 padding overhead

MAX_MESSAGE_LENGTH = MAX_RSA_KEY_SIZE_BYTES - PADDING_OVERHEAD

# Create a string of 117 characters
message = ''.join(str(i) for i in range(63))

# Function to check if the message can be encrypted
def can_encrypt(message):
    if len(message) > MAX_MESSAGE_LENGTH:
        print(f"Message too large: {len(message)} vs max_message_length={MAX_MESSAGE_LENGTH}")
        print(message)
        return
    print(f"Message good: {len(message)} vs max_message_length={MAX_MESSAGE_LENGTH}")

can_encrypt(message)

with open(os.path.join('../key/public.pem'), 'rb') as f:
    pub_key = rsa.PublicKey.load_pkcs1(f.read())

try:
    enc_mg = rsa.encrypt(message.encode(encoding="utf-8"), pub_key)
    print(enc_mg)
except Exception as e:
    print(f"Error encoding: {e=}")