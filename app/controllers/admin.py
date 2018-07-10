import functools
from uuid import uuid4

from flask import (
	Blueprint, g, request, Response, jsonify, flash, redirect, render_template, session, url_for,
	current_app as app, jsonify
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
			flash("Please login to carry out request", "info")
			return redirect(url_for(".login"))
		else:
			return view(**kwargs)

	return wrapped_view	


@bp.before_request
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
		return redirect(url_for(".home"))
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
	return redirect(url_for(".login"))


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

			return redirect(url_for(".home"))
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
		err = validate.validate_create_agent_web(request.form)
		if err:
			flash(err, "danger")
			return render_template("admin/invite.html")
		# Try to get agent if exists, if not create new
		agent = Agent.find_one({"phone": request.form["phone"]})
		msg = None
		if agent is None:
			data = {
				"name": request.form["name"],
				"phone": request.form["phone"],
				"confirmed": 0,
				"confirm_code": str(uuid4())
			}
			agent = Agent(data)
			agent.save()
			confirm_url = url_for("agent.confirm", code=agent.confirm_code)
			app.logger.info("Agent conformation link ({0}): {1}\n".format(agent.phone, confirm_url))
			msg = "Agent account created successfully. Check confirm link in logs."
		
		invite = admin.get_invite(agent)
		if invite is not None:
			msg = "Agent is already in your list" if invite.accepted else "Agent is still yet to accept your invite"
			flash(msg, "info")
			return redirect(url_for(".home"))
		
		invite = AdminAgent({
			"admin_id": admin.id,
			"agent_id": agent.id,
			"accepted": 0
		})
		invite.save()
		if msg is None:
			msg = "Agent invitation sent successfully"
		flash(msg, "success")
		return redirect(url_for(".home"))

	else:
		return render_template("admin/invite.html")


@bp.route("/remove_agent", methods=("POST",))
@login_required
def remove_agent():
	agent_id = request.form.get("agent_id")
	if not agent_id or not Agent.find_one(agent_id):
		msg = "Error with your request"
		status = False
		flash(msg, "danger")
	else:
		ad_ag = AdminAgent.find_one({
			"admin_id": g.user.id,
			"agent_id": agent_id
		})
		if ad_ag is not None:
			ad_ag.delete()
		msg = "Agent removed successfully"
		status = True
		flash(msg, "success")
	return jsonify({
		"status": status,
		"message": msg
	})


@bp.route("/logout", methods=("GET",))
def logout():
	""" General logout for both admins and agents """
	user_type = "admin"
	if getattr(g, "type") == "agent":
		user_type = "agent"
	session.clear()
	flash("Logout successful", "info")
	return redirect(url_for("{0}.login".format(user_type)))

