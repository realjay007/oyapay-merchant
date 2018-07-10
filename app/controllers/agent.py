import functools

from flask import (
	Blueprint, g, request, Response, jsonify, flash, redirect, render_template, session, url_for,
	current_app as app
)
from werkzeug.security import check_password_hash, generate_password_hash
import simplejson

from ..models import (
	Admin, Agent, AdminAgent
)
from ..libraries import (
	validate
)

bp = Blueprint("agent", __name__, url_prefix="/agent")

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			flash("Please login to carry out request", "info")
			return redirect(url_for("agent.login"))
		else:
			return view(**kwargs)

	return wrapped_view


@bp.before_request
def load_logged_in_user():
	agent_id = session.get("agent_id")

	if agent_id is None:
		g.user = None
		g.type = None
	else:
		g.user = Agent.find_one(agent_id)
		g.type = "agent"


@bp.route("/confirm/<code>", methods=("GET", "POST"))
def confirm(code):
	if g.user is not None:
		return redirect(url_for("agent.home"))
	
	agent = Agent.find_one({"confirm_code": code})
	if agent is None:
		flash("Invalid confirmation link", "danger")
		return redirect(url_for("agent.login"))
	elif agent.confirmed:
		flash("Account already confirmed", "info")
		return redirect(url_for("agent.login"))
	
	if request.method == "GET":
		return render_template("agent/confirm.html", code=code)
	else:
		err = validate.validate_confirm_agent(request.form)
		if err:
			flash(err, "danger")
			return render_template("agent/confirm.html", code=code)
		agent.password = generate_password_hash(request.form["password"])
		agent.confirmed = 1
		agent.save()

		flash("Confirmation successful. Please login to continue", "success")
		return redirect(url_for("agent.login"))


@bp.route("/login", methods=("GET", "POST"))
def login():
	if request.method == "POST":
		err = validate.validate_login_agent(request.form)
		if err:
			flash(err, "danger")
			return render_template("agent/login.html")
		else:
			phone = request.form["phone"]
			agent = Agent.find_one({"phone": phone})
			session.clear()
			session["agent_id"] = agent.id
			flash("Login succesful", "success")

			return redirect(url_for("agent.home"))
	else:
		return render_template("agent/login.html")


@bp.route("/home", methods=("GET",))
@login_required
def home():
	agent = g.user
	admins = agent.get_admins(True)
	invite_count = agent.count_invites()
	return render_template("agent/home.html", agent=agent, admins=admins, invite_count=invite_count)


@bp.route("/pending", methods=("GET",))
@login_required
def pending():
	agent = g.user
	admins = agent.get_admins(False)
	return render_template("agent/pending.html", agent=agent, admins=admins)


@bp.route("/accept/<invite_id>", methods=("GET",))
@login_required
def accept(invite_id):
	ad_ag = AdminAgent.find_one(invite_id)
	if ad_ag is None or g.user.id != ad_ag.agent_id:
		flash("Error with request", "danger")
	else:
		ad_ag.accepted = 1
		ad_ag.save()
		flash("Invitation accepted successfully", "success")
	return redirect(url_for(".home"))


@bp.route("/decline/<invite_id>", methods=("GET",))
@login_required
def decline(invite_id):
	ad_ag = AdminAgent.find_one(invite_id)
	if ad_ag is None or g.user.id != ad_ag.agent_id:
		flash("Error with request", "danger")
	else:
		ad_ag.delete()
		flash("Invitation declined successfully", "success")
	return redirect(url_for(".home"))


@bp.route("/remove_admin", methods=("POST",))
@login_required
def remove_admin():
	admin_id = request.form.get("admin_id")
	if not admin_id or not Admin.find_one(admin_id):
		msg = "Error with your request"
		status = False
		flash(msg, "danger")
	else:
		ad_ag = AdminAgent.find_one({
			"admin_id": admin_id,
			"agent_id": g.user.id
		})
		if ad_ag is not None:
			ad_ag.delete()
		msg = "Business removed successfully"
		status = True
		flash(msg, "success")
	return jsonify({
		"status": status,
		"message": msg
	})

