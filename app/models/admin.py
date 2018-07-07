from pypika import Query, Table, Field

from .model import Model
from .agent import Agent
from .admin_agent import AdminAgent

class Admin(Model):
	""" Admin model class"""

	_table = "admins"

	_fields = ("id", "name", "phone", "password", "biz_name", "pass", "created_at")
	

	def get_data(self) -> dict:
		""" Override parent method to exclude password field """
		return super().get_data(("password",))
	

	def get_agents(self, accepted=None) -> list:
		""" Get agents under admin
				set accepted to True to return only agents with accepted invites, false for non-accepted
		"""
		sub_select = Query.from_(AdminAgent._table).select("agent_id") \
			.where(Field("admin_id") == self.id)
		
		if accepted is not None:
			sub_select = sub_select.where(Field("accepted") == accepted)
		
		q = Query.from_(Agent._table).select("*") \
			.where(Field("id").isin(sub_select))
		
		raw_agents = self._db.execute(q.get_sql())
		
		agents = []
		if raw_agents is not None:
			for raw_agent in raw_agents:
				agents.append(Agent(raw_agent))
		
		return agents
	

	def has_agent(agent) -> bool:
		""" Check if admin is assoc with agent
		
			:param agent -> Agent model or agent id
		"""
		if isinstance(agent, Agent):
			agent_id = agent.id
		else:
			agent_id = agent
		
		assoc = AdminAgent.find_many({"admin_id": self.id, "agent_id": agent_id})

		return bool(assoc)





