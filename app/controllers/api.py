import functools

from flask import (
	Blueprint, g, request, Response, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
import simplejson

from ..models import (
	Admin, Agent, AdminAgent
)

bp = Blueprint("api", __name__, url_prefix="/api")

def json_response(output):
	output = simplejson.dumps(output, for_json=True)
	resp = Response(output, mimetype="application/json")
	return resp


@bp.route("/admins", methods=("POST",))
def create_admin():
	""" Create admin profile """
	data = {
		"name": request.form.get("name"),
		"phone": request.form.get("phone"),
		"password": generate_password_hash(request.form.get("password")),
		"biz_name": request.form.get("biz_name"),
		"pass": request.form.get("pass", "")
	}

	admin = Admin(data)
	admin.save()
	output = {
		"status": True,
		"message": "Admin created successfully",
		"data": admin
	}
	return json_response(output)


@bp.route("/admins", methods=("GET",))
def get_admins():
	admins = Admin.find_many(request.args)
	output = {
		"status": True,
		"data": admins
	}
	return json_response(output)


@bp.route("/admins/<int:id>", methods=("GET",))
def get_admin_by_id(id):
	admin = Admin.find_one(id)

	if admin is None:
		return not_found()
	
	return json_response({
		"status": True,
		"data": admin
	})


@bp.route("/admins/<int:id>", methods=("PUT", "PATCH"))
def update_admin(id):
	admin = Admin.find_one(id)

	if admin is None:
		return not_found()

	for field in ["name", "phone", "biz_name", "pass"]:
		setattr(admin, field, request.form.get(field, getattr(admin, field)))
	admin.save()

	output = {
		"status": True,
		"message": "Admin edited successfully",
		"data": admin
	}

	return json_response(output)


@bp.route("/admins/<int:id>", methods=("DELETE",))
def delete_admin(id):
	admin = Admin.find_one(id)
	if admin is None:
		return not_found

	admin.delete()

	output = {
		"status": True,
		"message": "Admin deleted successfully"
	}
	return jsonify(output)


@bp.route("/agents", methods=("POST",))
def create_agent():
	data = {
		"name": request.form.get("name"),
		"phone": request.form.get("phone"),
		"password": generate_password_hash(request.form.get("password")),
		"confirmed": 1
	}

	agent = Agent(data)
	agent.save()
	output = {
		"status": True,
		"message": "Agent created successfully",
		"data": agent
	}
	return json_response(output)


@bp.route("/agents", methods=("GET",))
def get_agents():
	agents = Agent.find_many(request.args)
	output = {
		"status": True,
		"data": agents
	}
	return json_response(output)


@bp.route("/agents/<int:id>", methods=("GET",))
def get_agent_by_id(id):
	agent = Agent.find_one(id)

	if agent is None:
		return not_found()
	
	return json_response({
		"status": True,
		"data": agent
	})


@bp.route("/agents/<int:id>", methods=("PUT", "PATCH"))
def update_agent(id):
	agent = Agent.find_one(id)

	if agent is None:
		return not_found()

	for field in ["name", "phone"]:
		setattr(agent, field, request.form.get(field, getattr(agent, field)))
	agent.save()

	output = {
		"status": True,
		"message": "Agent edited successfully",
		"data": agent
	}

	return json_response(output)


@bp.route("/agents/<int:id>", methods=("DELETE",))
def delete_agent(id):
	agent = Agent.find_one(id)
	if agent is None:
		return not_found

	agent.delete()
	output = {
		"status": True,
		"message": "Agent deleted successfully"
	}
	return jsonify(output)


@bp.route("/assoc", methods=("POST",))
def create_assoc():
	admin_id = request.form.get("admin_id")
	agent_id = request.form.get("agent_id")

	assoc = AdminAgent({
		"admin_id": admin_id,
		"agent_id": agent_id,
		"accepted": 1
	})
	assoc.save()

	output = {
		"status": True,
		"message": "Association created successfully"
	}
	return jsonify(output)


@bp.route("/assoc", methods=("DELETE",))
def delete_assoc():
	admin_id = request.form.get("admin_id")
	agent_id = request.form.get("agent_id")

	assoc = AdminAgent.find_one({
		"admin_id": admin_id,
		"agent_id": agent_id
	})
	if assoc is None:
		return not_found("No associations with sent ids found")
	
	assoc.delete()
	output = {
		"status": True,
		"message": "Association deleted successfully"
	}
	return jsonify(output)


@bp.route("/admin/<int:id>/agents", methods=("GET",))
def get_admin_agents(id):
	admin = Admin.find_one(id)

	if admin is None:
		return not_found("No admin with this id exist")
	
	agents = admin.get_agents()
	output = {
		"status": True,
		"data": agents
	}
	return json_response(output)


@bp.errorhandler(404)
def not_found(error=None):
	output = {
		"status": False,
		"message": error or "Resource not found " + request.url
	}
	resp = jsonify(output)
	resp.status_code = 404
	return resp



