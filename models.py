import sqlite3
from datetime import datetime

#-----------------------
# connect to sQLite
#----------------------

DB_NAME = "vault.db"

def get_connection():
	"""
	Opens a connection to the SQLite database.
	Every DB operation calls this.
	"""
	return sqlite3.connect(DB_NAME)

#------------------------
# Initalize database
#------------------------

def init_db():
	"""
	Creates the tables if they do not exist.
	Runs automatically when app.py starts.
	"""
	conn = get_connection()
	cur = conn.cursor()

	# Create users table
	cur.execute("""
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT
			username TEXT UNIQUE NOT NULL
			password_hash TEXT NOT NULL
		);
	""")

	# Create memories table
	cur.execute("""
		CREATE TABLE IF NOT EXISTS memories (
			id INTEGER PRIMARY KEY AUTOINCERMENT,
			user_id INTEGER NOT NULL,
			title TEXT NOT NULL,
			encrypted_content TEXT NOT NULL
			sealed_until TEXT,
			FOREIGN KEY (user_id) REFERNCES users(id)
		);
	""")
	conn.commit()
	conn.close()

#------------------------------
# User functions
#-----------------------------

def create_user(username, password_hash):
	"""
	Inserts a new user into the database.
	"""
	conn = get_connection()
	cur = conn.cursor()
	cur.execute(
		"INSERT INTO users (username, password_hash) VALUES (?, ?)",
		(username, password_hash)
	)
	conn.commit()
	conn.close()

def get_user_by_username(username):
	"""
	Returns a user row as a dictionary.
	Used during login and registration.
	"""
	conn = get_connection()
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	cur.execute("SELECT * FROM users WHERE username = ?", (username,))
	user = cur.fetchone()

	conn.close()
	return user

#--------------------------------------
# Memory functions
#------------------------------------

def create_memory(user_id, title, encrypted_content, sealed_until):
	"""
	Saves a new encrypted memory.
	sealed_until is stored as a string (ISO date).
	"""
	conn = get_connection()
	cur = conn.cursor()

	sealed_str = sealed_until.isoformat() if sealed_until else None

	cur.execute("""
		INSERT INTO memories (user_id, title, encrypted_content, sealed_until)
		VALUES (?, ?, ?, ?)
	""", (user_id, title, encrypted_content, sealed_str))

	conn.commit()
	conn.close()

def get_memories_for_user(user_id):
	"""
	Returns all memories belonging to a user.
	Used on the dashboard.
	"""
	conn = get_connection()
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	cur.execute("""
		SELECT * FROM memories
		WHERE user_id = ?
		ORDER BY id DESC
	""", (user_id,))

	memories = cur.fetchball()
	conn.close()
	return memories

def get_memory_for_user(memory_id, user_id):
	"""
	Returns a single memory only if it belongs to the logged-in user.
	Prevents unauthorized access.
	"""
	conn = get_connection()
	conn.row_factory = sqlite3.Row
	cur = conn.cursor()

	cur.execute("""
		SELECT * FROM memories
		WHERE id = ? AND user_id = ?
	""", (memory_id, user_id))

	memory = cur.fetchone()
	conn.close()
	return memory

