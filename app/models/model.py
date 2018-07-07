from ..db import get_db
from pypika import Query, Table, Field

class Model:
	""" Base model class """

	# Model fields
	_fields = ("id")

	# Table name
	_table = "model"

	# Database
	_db = get_db()

	def __init__(self, params: dict = {}, exclude = ()):
		""" Class constructor """
		self.init_data(params, exclude)
	

	def init_data(self, params: dict = {}, exclude = ()):
		""" Initialise model properties """
		for key, value in params.items():
			# _fields must be defined in child model
			if key in self._fields and key not in exclude:
				setattr(self, key, value)


	def get_data(self, exclude = ()) -> dict:
		""" Get a dict of object data """
		data = {}
		for key, value in vars(self).items():
			if key in self._fields and key not in exclude:
				data[key] = value
		return data


	def save(self, exclude = ()):
		""" Save model to db, inserting if id does not exist, updating if otherwise """
		data = self.get_data(("id",)+exclude)
		keys = data.keys()
		values = data.values()
		cur = self._db.cursor()
		if hasattr(self, "id"):
			# Update operation
			q = Query.update(self._table).set(data).where(Field("id") == self.id)
			sql = q.get_sql()
			cur.execute(sql)
		else:
			# Insert operation
			q = Query.into(self._table).columns(*keys).insert(*values)
			cur.execute(q.get_sql())
			self.id = cur.lastrowid
		self._db.commit()

		return self
	

	def delete(self):
		""" Delete object from db """
		self._db.execute(f"DELETE FROM {self._table} WHERE id = ?", (self.id,))
		self._db.commit()


	@staticmethod
	def find_one(query):
		""" Fetch a record from db """
		if type(query) is str or type(query) is int:
			query = {"id": query}

		q = Query.from_(self._table).select("*")

		for key, value in query.items():
			q = q.where(Field(key) == value)

		sql = q.get_sql()

		obj = self._db.execute(sql).fetchone()
		if obj is not None:
			obj = self.__class__(obj)
		return obj


	@staticmethod
	def find_many(query):
		""" Fetch array of records from db """
		if type(query) is str or type(query) is int:
			query = {"id": query}
		
		q = Query.from_(self._table).select("*")

		for key, value in query.items():
			q = q.where(Field(key) == value)

		sql = q.get_sql()

		objs = self._db.execute(sql).fetchall()
		result = []
		if objs is not None:
			for obj in objs:
				result.append(self.__class__(obj))
		return result

