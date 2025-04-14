from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_OAEP

def decrypt_file(encrypted_path, private_key_path):
    with open(encrypted_path, "rb") as f:
        enc_session_key = f.read(256)   # RSA-encrypted session key (2048-bit RSA = 256 bytes)
        nonce = f.read(16)              # AES nonce (16 bytes)
        tag = f.read(16)                # AES tag (16 bytes)
        ciphertext = f.read()          # Rest is AES-encrypted data

    # Load private RSA key
    with open(private_key_path, "rb") as f:
        private_key = RSA.import_key(f.read())

    # Decrypt session key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt data with AES
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    data = cipher_aes.decrypt_and_verify(ciphertext, tag)

    # Write output
    output_path = encrypted_path.replace(".enc", ".zip")
    with open(output_path, "wb") as f:
        f.write(data)

    print(f"[+] Decrypted file → {output_path}")

# Example usage:
decrypt_file("Your path file : ", "private.pem")
