from ..db import get_db
from pypika import Query, Table, Field

class Model:
	""" Base model class """

	# Model fields
	_fields = ("id")

	# Table name
	_table = "model"

	# Database
	_db = None

	@staticmethod
	def init_db():
		""" Initialise db connection """
		if Model._db is None:
			Model._db = get_db()
		return Model._db

	def __init__(self, params: dict = {}, exclude = ()):
		""" Class constructor """
		self.init_data(params, exclude)
		self.init_db()
	

	def init_data(self, params: dict = {}, exclude = ()):
		""" Initialise model properties """
		for key, value in params.items():
			# _fields must be defined in child model
			if key in self._fields and key not in exclude:
				setattr(self, key, value)


	def get_data(self, exclude = ()) -> dict:
		""" Get a dict of object data """
		data = {}
		for key in self._fields:
			if hasattr(self, key) and key not in exclude:
				data[key] = getattr(self, key)
		return data
	

	def for_json(self):
		""" Return json serializable form of model """
		return self.get_data()


	def save(self, exclude = ()):
		""" Save model to db, inserting if id does not exist, updating if otherwise """
		data = self.get_data(("id",)+exclude)
		keys = data.keys()
		values = data.values()
		cur = self._db.cursor()
		if hasattr(self, "id"):
			# Update operation
			q = Query.update(self._table)
			for key, value in data.items():
				q = q.set(key, value)
			q = q.where(Field("id") == self.id)
			sql = q.get_sql()
			cur.execute(sql)
		else:
			# Insert operation
			q = Query.into(self._table).columns(*keys).insert(*values)
			cur.execute(q.get_sql())
			self.id = cur.lastrowid
			# Sync to get table defaults
			self.init_data(self.__class__.find_one(self.id).get_data())
		self._db.commit()

		return self
	

	def delete(self):
		""" Delete object from db """
		self._db.execute(f"DELETE FROM {self._table} WHERE id = ?", (self.id,))
		self._db.commit()


	@classmethod
	def find_one(cls, query):
		""" Fetch a record from db """
		if type(query) is str or type(query) is int:
			query = {"id": query}

		q = Query.from_(cls._table).select("*")

		for key, value in query.items():
			q = q.where(Field(key) == value)

		sql = q.get_sql()
		db = Model.init_db()
		obj = db.execute(sql).fetchone()
		if obj is not None:
			obj = cls(obj)
		return obj


	@classmethod
	def find_many(cls, query, limit = 0, offset = 0):
		""" Fetch array of records from db """
		if type(query) is str or type(query) is int:
			query = {"id": query}
		
		q = Query.from_(cls._table).select("*")

		for key, value in query.items():
			q = q.where(Field(key) == value)
		q = q.offset(offset)
		if limit > 0:
			q = q.limit(limit)
		sql = q.get_sql()

		db = Model.init_db()
		objs = db.execute(sql).fetchall()
		result = []
		if objs is not None:
			for obj in objs:
				result.append(cls(obj))
		return result

