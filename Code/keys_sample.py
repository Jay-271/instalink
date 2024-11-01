import rsa

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