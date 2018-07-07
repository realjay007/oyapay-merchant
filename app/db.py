import sqlite3, click

from flask import current_app, g
from flask.cli import with_appcontext

def init_app(app):
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command)

def get_db():
	if "db" not in g:
		g.db = sqlite3.connect(
			current_app.config["DATABASE"],
			detect_types=sqlite3.PARSE_DECLTYPES,
			check_same_thread=False
		)
		g.db.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
	
	return g.db


def close_db(e=None):
	db = g.pop("db", None)

	if db is not None:
		# No need to close db since all requests share one connection
		# db.close()
		pass


def init_db():
	db = get_db()

	with current_app.open_resource("schema.sql") as f:
		db.executescript(f.read().decode("utf-8"))
	

@click.command("init-db")
@with_appcontext
def init_db_command():
	"""Clear the existing data and create new tables"""
	init_db()
	click.echo("Initialized the database")

