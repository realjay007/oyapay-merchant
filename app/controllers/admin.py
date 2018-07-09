import functools

from flask import (
	Blueprint, g, request, Response, jsonify, flash, redirect, render_template, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
import simplejson

from ..models import (
	Admin, Agent, AdminAgent
)
from ..libraries import (
	validate
)

bp = Blueprint("admin", __name__)

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for("admin.login"))
		else:
			return view(**kwargs)

	return wrapped_view	


@bp.before_app_request
def load_logged_in_user():
	admin_id = session.get("admin_id")

	if admin_id is None:
		g.user = None
		g.type = None
	else:
		g.user = Admin.find_one(admin_id)
		g.type = "admin"


@bp.route("/", methods=("GET",))
def register_page():
	if g.user is not None:
		return redirect(url_for("admin.home"))
	else:
		return render_template("admin/register.html")


@bp.route("/register", methods=("POST", "GET"))
def register():
	if request.method == "GET":
		return render_template("admin/register.html")
	err = validate.validate_create_admin(request.form)
	if err:
		flash(err, "danger")
		return render_template("admin/register.html")
	
	data = {
		"name": request.form.get("name"),
		"phone": request.form.get("phone"),
		"password": generate_password_hash(request.form.get("password")),
		"biz_name": request.form.get("biz_name"),
		"pass": request.form.get("pass", "")
	}

	admin = Admin(data)
	admin.save()
	flash("Registration successful. Pls login to continue", "success")
	return redirect(url_for("admin.login"))


@bp.route("/login", methods=("GET", "POST"))
def login():
	if request.method == "POST":
		err = validate.validate_login_admin(request.form)
		if err:
			flash(err, "danger")
			return render_template("admin/login.html")
		else:
			phone = request.form["phone"]
			admin = Admin.find_one({"phone": phone})
			session.clear()
			session["admin_id"] = admin.id
			flash("Login succesful", "success")

			return redirect(url_for("admin.home"))
	else:
		return render_template("admin/login.html")


@bp.route("/home", methods=("GET",))
@login_required
def home():
	admin = g.user
	agents = admin.get_agents(True)
	return render_template("admin/home.html", admin=admin, agents=agents)


@bp.route("/invite", methods=("GET", "POST"))
@login_required
def invite():
	admin = g.user
	if request.method == "POST":
		return render_template("admin/invite.html")
	else:
		return render_template("admin/invite.html")


@bp.route("/logout", methods=("GET",))
def logout():
	""" General logout for both admins and agents """
	user_type = "admin"
	if getattr(g, "type") == "agent":
		user_type = "agent"
	session.clear()
	flash("Logout successful", "info")
	return redirect(url_for("{0}.login".format(user_type)))

