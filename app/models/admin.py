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
		sub_select = Query.from_(admin_agent.AdminAgent._table).select("agent_id") \
			.where(Field("admin_id") == self.id)
		
		if accepted is not None:
			sub_select = sub_select.where(Field("accepted") == int(accepted))
		
		q = Query.from_(agent.Agent._table).select("*") \
			.where(Field("id").isin(sub_select))
		
		raw_agents = self._db.execute(q.get_sql())
		
		agents = []
		if raw_agents is not None:
			for raw_agent in raw_agents:
				agents.append(agent.Agent(raw_agent))
		
		return agents
	

	def has_agent(ag) -> bool:
		""" Check if admin is assoc with agent
		
			:param agent -> Agent model or agent id
		"""
		if isinstance(ag, agent.Agent):
			agent_id = ag.id
		else:
			agent_id = ag
		
		assoc = admin_agent.AdminAgent.find_many({"admin_id": self.id, "agent_id": agent_id})

		return bool(assoc)


	def for_json(self):
		""" Return json serializable form of model, remove password field """
		return self.get_data(("password",))


