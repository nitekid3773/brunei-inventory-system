# generate_key.py
from cryptography.fernet import Fernet

# Generate a secure key
key = Fernet.generate_key()

# Decode to string and print
key_string = key.decode()
print("\n" + "="*50)
print("YOUR ENCRYPTION KEY:")
print("="*50)
print(key_string)
print("="*50)
print("\nCopy this key and add it to your .streamlit/secrets.toml file:")
print(f'ENCRYPTION_KEY = "{key_string}"')
print("="*50)
