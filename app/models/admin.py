from pypika import Query, Table, Field

from .model import Model
from . import agent
from . import admin_agent

class Admin(Model):
	""" Admin model class"""

	_table = "admins"

	_fields = ("id", "name", "phone", "password", "biz_name", "pass", "created_at")
	

	def get_agents(self, accepted=None) -> list:
		""" Get agents under admin
				set accepted to True to return only agents with accepted invites, false for non-accepted
		"""
		# Get invites
		q = Query.from_(admin_agent.AdminAgent._table).select("*") \
			.where(Field("admin_id") == self.id)
		if accepted is not None:
			q = q.where(Field("accepted") == int(accepted))

		raw_invites = self._db.execute(q.get_sql())
		invites = {}
		if raw_invites is not None:
			for raw_invite in raw_invites:
				invites[raw_invite["agent_id"]] = admin_agent.AdminAgent(raw_invite)

		# Get agents
		q = Query.from_(agent.Agent._table).select("*") \
			.where(Field("id").isin(list(invites.keys())))
		
		raw_agents = self._db.execute(q.get_sql())
		agents = []
		if raw_agents is not None:
			for raw_agent in raw_agents:
				ag = agent.Agent(raw_agent)
				ag.invite = invites[ag.id]
				agents.append(ag)
		
		return agents
	

	def get_invite(self, ag):
		""" Get invite that connects agent and admin if any """
		if isinstance(ag, agent.Agent):
			agent_id = ag.id
		else:
			agent_id = ag

		return admin_agent.AdminAgent.find_one({"admin_id": self.id, "agent_id": agent_id})
	

	def has_agent(self, ag) -> bool:
		""" Check if admin is assoc with agent
		
			:param agent -> Agent model or agent id
		"""
		return bool(self.get_invite())


	def for_json(self):
		""" Return json serializable form of model, remove password field """
		return self.get_data(("password",))


