from pypika import Query, Field, Table

from .model import Model
from .admin import Admin
from .admin_agent import AdminAgent

class Agent(Model):
	""" Agent model class """

	_table = "agents"

	_fields = ("id", "name", "phone", "password", "confirmed", "created_at")


	def get_data(self) -> dict:
		""" Override parent method to exclude password field """
		return super().get_data(("password",))
	

	def get_admins(self, accepted=None) -> list:
		""" Get admins associated with agent,
				set accepted to True to return only admins with accepted invites, false for non-accepted
		"""
		sub_select = Query.from_(AdminAgent._table).select("admin_id") \
			.where(Field("agent_id") == self.id)
		
		if accepted is not None:
			sub_select = sub_select.where(Field("accepted") == accepted)
		
		q = Query.from_(Admin._table).select("*") \
			.where(Field("id").isin(sub_select))
		
		raw_admins = self._db.execute(q.get_sql())
		
		admins = []
		if raw_admins is not None:
			for raw_admin in raw_admins:
				admins.append(Agent(raw_admin))
		
		return admins
	

	def has_admin(admin) -> bool:
		""" Check if agent is assoc with admin
		
			:param admin -> Admin model or admin id
		"""
		if isinstance(admin, Admin):
			admin_id = admin.id
		else:
			admin_id = admin
		
		assoc = AdminAgent.find_many({"agent_id": self.id, "admin_id": admin_id})

		return bool(assoc)


