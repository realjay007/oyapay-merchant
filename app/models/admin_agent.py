from .model import Model
from .agent import Agent
from .admin import Admin

class AdminAgent(Model):
	""" Admin-agent intermediary model """

	_table = "admin_agents"

	_fields = ("admin_id", "agent_id", "invited_at", "accepted")



