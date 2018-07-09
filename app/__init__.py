import os

from flask import Flask
import logging
from logging.handlers import RotatingFileHandler

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY="dev",
		DATABASE=os.path.join(app.instance_path, "app.sqlite"),
	)

	if test_config is None:
		# Load the instance config, if it exists, when not testing
		app.config.from_pyfile("config.py", silent=True)
	else:
		# Load the test config if passed in
		app.config.from_mapping(test_config)
	
	# ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError as os_error:
		pass
	
	log_handler = RotatingFileHandler("merchant.log", maxBytes=1024000, backupCount=1)
	log_handler.setLevel(logging.INFO)
	app.logger.addHandler(log_handler)
	
	# a simple page that says hello
	@app.route("/hello")
	def hello():
		app.logger.info("App tested successfully")
		return "Hello, World"
	
	from . import db
	db.init_app(app)

	from .controllers import api, admin
	app.register_blueprint(api.bp)
	app.register_blueprint(admin.bp)

	
	return app
