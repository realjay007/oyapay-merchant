import functools

from flask import (
	Blueprint, g, request
)
from werkzeug.security import check_password_hash, generate_password_hash

from ..models.admin import Admin, AdminAgent, Agent

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/admins", methods=("POST"))
def create_admin():
	""" Create admin profile """
	pass

