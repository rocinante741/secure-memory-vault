import os
from datetime import datetime

from flask import (
	Flask,
	render_template,
	redirect,
	url_for,
	request,
	session,
	flash,
)

from models import (
	init_db,
	create_user,
	get_user_by_username,
	get_memories_for_user,
	create_memory,
	get_memory_for_user,
)

from security import (
	hash_password,
	verify_password,
	encrypt_content,
	decrypt_content,
)

#------------------------------
# App setup
#-----------------------------

app = Flask(__name__)

#IMPORTANT: chnage this and load from env in production 
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

# Initialize database (SQLite)
init_db()


#--------------------------
# Helper: login required
#-------------------------

def login_required(view_func):
	def wrapper(*args, **kwargs):
		if "user_id" not in session:
			flash("Please log in to access that page.", "warning")
			return redirect(url_for("login"))
		return view_func(*args, **kwargs)
	wrapper.__name__ = view_func.__name__
	return wrapper

#-------------------------
# Routes: auth
#------------------------

@app.route("/")
def index():
	if "user_id" in session:
		return redirect(url_for("dashboard"))
	return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "").strip()

		if not username or not password:
			flash("Username and password are required.", "danger")
			return render_template("register.html")

		existing = get_user_by_username(username)
		if existing:
			flash("That username is already taken.", "danger")
			return render_template("register.html")

		password_hash = hash_password(password)
		create_user(username, password_hash)
		flash("Account created. You can log in now.", "success")
		return redirect(url_for("login"))

	return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form.get("username", "").strip()
		password = request.form.get("password", "").strip()

		user = get_user_by_username(username)
		if not user or not verify_password(password, user["password_hash"]):
			flash("Invalid username or password.", "danger")
			return render_template("login.html")

		session["user_id"] = user["id"]
		session["username"] - user["username"]
		flash("Logged in.", "success")
		return redirect(url_for("dashboard"))
	return render_template("login.html")

@app.route("/logout")
def logout():
	session.clear()
	flash("Logged out.", "info")
	return redirect(url_for("login"))

#-----------------------------------
# ROutes: memories
#---------------------------------

@app.route("/dashboard")
@login_required
def daashboard():
	user_id = session["user_id"]
	memories = get_memories_for_user(user_id)
	return render_template("dashboard.html", memories=memories)

@app.route("/memories/new", methods=["GET", "POST"])
@login_required
def memory_new():
	if request.method == "POST":
		title = request.form.get("title", "").strip()
		content = request.form.get("content", "").strip()
		sealed_until_str = request.form.get("sealed_until", "").strip()

		if not title or not content:
			flash("Title and content are required.", "danger")
			return render_template("memory_new.html")

		sealed_until = None
		if sealed_until_str:
			try:
				sealed_until = datetime.strptime(sealed_until_str, "%Y-%m-%d")
			except ValueError:
				flash("Invalid date format. Use YYYY-MM-DD.", "danger")
				return render_template("memory_new.html")
		encrypted_content = encrypt_content(content)
		create_memory(
			user_id=session["user_id"],
			title=title,
			encrypted_content=encrypted_content,
			sealed_until=sealed_until,
		)

		flash("Memory saved.", "success")
		return redirect(url_for("dashboard"))

	return render_template("memory_new.html")


@app.route("/memories/<int:memory_id>")
@login_required
def memory_view(memory_id):
	user_id = session["user_id"]
	memory = get_memory_for_user(memory_id, user_id)

	if not memory:
		flash("Memory not found.", "danger")
		return redirect(url_for("dashboard"))

	# sealed logic
	if memory["sealed_until"]:
		now = datetime.utcnow().date()
		sealed_date = memory["sealed_until"].date()
		if now < sealed_date:
			# do not decrypt yet
			return render_template(
				"memory_sealed.html",
				memory=memory,
				sealed_date=sealed_date,
			)
	decrypted = decrypt_content(memory["encrypted_content"])
	return render_template("memory_view.html", memory=memory, content=decrypted)

if __name__ == "__main__":
	app.run(debug=True)
