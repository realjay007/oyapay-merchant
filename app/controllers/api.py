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
	name = request.form.get("name")
	phone = request.form.get("phone")
	password = request.form.get("password")
	biz_name = request.form.get("biz_name")
	pass_field = request.form.get("pass", "")

	data = {
		"name": request.form.get("name"),
		"phone": request.form.get("phone"),
		"password": request.form.get("password"),
		"biz_name": request.form.get("biz_name"),
		"pass": request.form.get("pass", "")
	}
	data["password"] = generate_password_hash(data["password"])
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


@bp.errorhandler(404)
def not_found(error=None):
	output = {
		"status": False,
		"message": "Resource not found " + request.url
	}
	resp = jsonify(output)
	resp.status_code = 404
	return resp



