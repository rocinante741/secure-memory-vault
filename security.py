from dotenv import load_dotenv
import os
from passlib.hash import bcrypt
from cryptography.fernet import Fernet

#-----------------------------------=
# Load encryption key
#-----------------------------------

"""
This key MUST be stored in an environment variable.
Example:
export MEMORY_VAULT_KEY="your-generated-key"
"""

load_dotenv()

FERNET_KEY = os.environ.get("MEMORY_VAULT_KEY")

if not FERNET_KEY:
	raise RuntimeError("MEMORY_VAULT_KEY is not set in environment variables.")

fernet = Fernet(FERNET_KEY)

#----------------------------------------
# Password hashing
#---------------------------------------

def hash_password(plain_password):
	"""
	Hashes a password using bcrypt.
	Never store plaintext passwords.
	"""
	safe_password = plain_password[:72]
	return bcrypt.hash(safe_password)

def verify_password(plain_passsword, hashed_password):
	"""
	Verifies a password during login.
	"""
	safe_password = plain_password[:72]
	return bcrypt.verify(safe_password, hashed_password)

#-------------------------------------------
# Encryption helpers
#------------------------------------------

def encrypt_content(plain_text):
    """
    Encrypts memory content before storing it.
    """
    return fernet.encrypt(plain_text.encode()).decode()

def decrypt_content(cipher_text):
	"""
	Decrypts stored encrypted memory content.
	"""
	return fernet.decrypt(cipher_text.encode()).decode()
