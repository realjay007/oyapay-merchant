from .model import Model


class AdminAgent(Model):
	""" Admin-agent intermediary model """

	_table = "admin_agents"

	_fields = ("admin_id", "agent_id", "invited_at", "accepted")



