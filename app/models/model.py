from ..db import get_db

class Model:
	""" Base model class """

	# Model fields
	_fields = ()

	# Table name
	_table = ""

	# Database
	_db = get_db()

	def __init__(self, params: dict = {}):
		""" Class constructor """
		for key, value in params.items():
			# _fields must be defined in child model
			if key in self._fields:
				setattr(self, key, value)
	

	def get_data(self, exclude = ()) -> dict:
		""" Get a dict of object data """
		data = {}
		for key, value in vars(self).items():
			if key in self._fields and key not in exclude:
				data[key] = value
		return data


	def save(self):
		""" Save model to db, inserting if id does not exist, updating if otherwise """
		data = self.get_data(("id"))
		keys = data.keys()[:]
		values = data.values()[:]
		cur = self._db.cursor()
		if hasattr(self, "id"):
			# Update operation
			sql = (
				f"UPDATE {self._table}"
				" SET "+keys.join(" = ?, ").rstrp(", ")
				" WHERE id = ?"
			)
			values.append(self.id)
			cur.execute(sql, values)
		else:
			# Insert operation
			bind = "?, " * len(values)
			bind = bind.rstrip(", ")
			sql = (
				f"INSERT INTO {self._table}"
				" ("+keys.join(", ").rstrp(", ")+")"
				" VALUES ({0})".format(bind)
			)
			cur.execute(sql, values)
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
		keys = query.keys()[:]
		values = query.keys()[:]

		sql = (
			f"SELECT * FROM {self._table}"
			" WHERE "+keys.join(" = ?, ").rstrp(", ")
		)

		obj = self._db.execute(sql, values).fetchone()
		if obj is not None:
			obj = self.__class__(obj)
		return obj


	@staticmethod
	def find_many(query):
		""" Fetch array of records from db """
		if type(query) is str or type(query) is int:
			query = {"id": query}
		keys = query.keys()[:]
		values = query.keys()[:]

		sql = (
			f"SELECT * FROM {self._table}"
			" WHERE "+keys.join(" = ?, ").rstrp(", ")
		)

		objs = self._db.execute(sql, values).fetchall()
		result = []
		if objs is not None:
			for obj in objs:
				result.append(self.__class__(obj))
		return result

