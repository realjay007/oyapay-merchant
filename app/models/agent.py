from pypika import Query, Field, Table

from .model import Model
from . import admin
from . import admin_agent


class Agent(Model):
	""" Agent model class """

	_table = "agents"

	_fields = ("id", "name", "phone", "password", "confirmed", "confirm_code", "created_at")


	def get_admins(self, accepted=None) -> list:
		""" Get admins associated with agent,
				set accepted to True to return only admins with accepted invites, false for non-accepted
		"""
		# Get invites
		q = Query.from_(admin_agent.AdminAgent._table).select("*") \
			.where(Field("agent_id") == self.id)
		if accepted is not None:
			q = q.where(Field("accepted") == int(accepted))

		raw_invites = self._db.execute(q.get_sql())
		invites = {}
		if raw_invites is not None:
			for raw_invite in raw_invites:
				invites[raw_invite["admin_id"]] = admin_agent.AdminAgent(raw_invite)

		# Get admins
		q = Query.from_(admin.Admin._table).select("*") \
			.where(Field("id").isin(list(invites.keys())))
		
		raw_admins = self._db.execute(q.get_sql())
		admins = []
		if raw_admins is not None:
			for raw_admin in raw_admins:
				ad = admin.Admin(raw_admin)
				ad.invite = invites[ad.id]
				admins.append(ad)
		
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


	def count_invites(self) -> int:
		""" Count pending invitations """
		query = {
			"agent_id": self.id,
			"accepted": 0
		}
		return admin_agent.AdminAgent.count(query)


	def for_json(self):
		""" Return json serializable form of model, remove password field """
		return self.get_data(("password",))
