from pypika import Query, Field, Table

from .model import Model
from . import admin
from . import admin_agent


class Agent(Model):
	""" Agent model class """

	_table = "agents"

	_fields = ("id", "name", "phone", "password", "confirmed", "created_at")


	def get_admins(self, accepted=None) -> list:
		""" Get admins associated with agent,
				set accepted to True to return only admins with accepted invites, false for non-accepted
		"""
		sub_select = Query.from_(admin_agent.AdminAgent._table).select("admin_id") \
			.where(Field("agent_id") == self.id)
		
		if accepted is not None:
			sub_select = sub_select.where(Field("accepted") == int(accepted))
		
		q = Query.from_(admin.Admin._table).select("*") \
			.where(Field("id").isin(sub_select))
		
		raw_admins = self._db.execute(q.get_sql())
		
		admins = []
		if raw_admins is not None:
			for raw_admin in raw_admins:
				admins.append(admin.Admin(raw_admin))
		
		return admins
	

	def has_admin(adm) -> bool:
		""" Check if agent is assoc with admin
		
			:param admin -> Admin model or admin id
		"""
		if isinstance(adm, admin.Admin):
			admin_id = adm.id
		else:
			admin_id = adm
		
		assoc = admin_agent.AdminAgent.find_many({"agent_id": self.id, "admin_id": admin_id})

		return bool(assoc)


	def for_json(self):
		""" Return json serializable form of model, remove password field """
		return self.get_data(("password",))
