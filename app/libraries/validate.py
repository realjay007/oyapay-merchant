from ..models import Admin, Agent, AdminAgent
from flask import jsonify


def _required(form: dict, fields: list):
	"""Make sure form has specified fields"""
	for field in fields:
		value = form.get(field)
		if not value:
			return f"{field.capitalize()} field is required"
	return None


def _phone(value: str):
	"""Validate phone number"""
	if (not value.isnumeric()) or len(value) != 11:
		return "Invalid phone number"
	return None


def validate_create_admin(form: dict):
	"""Validate info sent when creating an admin, returns error message if any"""
	req_val = _required(form, ["name", "phone", "biz_name", "password"])
	if req_val:
		return req_val
	phone_val = _phone(form["phone"])
	if phone_val:
		return phone_val
	if len(form["password"]) < 8:
		return "Password must be at least 8 characters"
	return None


def validate_create_agent(form: dict) -> str:
	"""Validate info sent when creating an agent, returns error message if any"""
	req_val = _required(form, ["name", "phone"])
	if req_val:
		return req_val
	phone_val = _phone(form["phone"])
	if phone_val:
		return phone_val
	return None


def validate_create_assoc(form: dict):
	"""Validate info sent when creating an admin-agent assoc, returns error message if any"""
	req_val = _required(form, ["admin_id", "agent_id"])
	if req_val:
		return req_val
	admin = Admin.find_one(form["admin_id"])
	agent = Agent.find_one(form["agent_id"])

	if admin is None:
		return "No admin with id {0} exists".format(form['admin_id'])
	elif agent is None:
		return "No agent with id {0} exists".format(form['agent_id'])
	else:
		return None


def send_val_error_as_json(error):
	"""Prepare validation error as a response object in json format"""
	resp = jsonify({
		"status": False,
		"message": error
	})
	resp.status_code = 400
	return resp
