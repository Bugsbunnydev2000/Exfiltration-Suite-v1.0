# Exfiltration-Suite-v1.0
A simple Exfiltration  Malware

**🧩 Modules**: 

📁 1. dump.py
Extracts and zips sensitive data from a Windows machine.

📋 Clipboard: Reads current clipboard content.

📶 Wi-Fi Passwords: Extracts saved Wi-Fi profiles and cleartext passwords.

🔐 Chrome Passwords: Decrypts stored credentials using the system's master key.

🗜️ Zipping: Saves all collected data in a timestamped .zip file inside the dump/ directory.

🔒 Hybrid Encryption: Encrypts .zip using AES (for data) + RSA (for key).

📧 Emailing: Sends the encrypted dump to a remote address over secure SMTP.

-----------

**➡️ Requires:**

public.pem key to be present.

Gmail app password (2FA must be enabled).

-------------
**🔓 2. decode.py** : 

Decrypts the .enc file using the private key and restores the original .zip.

Uses PKCS1_OAEP + AES for decryption.

Output: Decrypted .zip file with all original data.

---------------

**🔑 3. generate_keys.py :**
Generates RSA 2048-bit public/private key pair:

private.pem: Keep this secure!

public.pem: Used to encrypt dump data.

------------------

**✅ How to Run** : 

```bash
pip install -r requirements.txt
```
🧪 1. Generate Keys

```bash
python generate_keys.py
```

🐇 2. Run Dumper (Target)

```bash
python dump.py
```

Creates encrypted .zip.enc in dump/

Sends to configured email


🔐 3. Decrypt (Receiver)

```bash
python decode.py
```

Enter paths to .enc file and private.pem

Output: .zip with extracted data


**Example :** 


https://github.com/user-attachments/assets/c30c2db5-aebf-4f7b-9e0c-ba3f1c1c55ad


