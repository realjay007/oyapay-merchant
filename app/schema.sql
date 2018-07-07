DROP TABLE IF EXISTS admins;
DROP TABLE IF EXISTS agents;
DROP TABLE IF EXISTS admin_agents;

CREATE TABLE admins (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	phone TEXT NOT NULL,
	password TEXT NOT NULL,
	biz_name TEXT NOT NULL,
	pass TEXT,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agents (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	phone TEXT NOT NULL,
	password TEXT NOT NULL,
	confirmed BOOLEAN DEFAULT 0,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admin_agents (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	admin_id INTEGER NOT NULL,
	agent_id INTEGER NOT NULL,
	invited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	accepted BOOLEAN DEFAULT 0,
	FOREIGN KEY (admin_id) REFERENCES admins (id),
	FOREIGN KEY (agent_id) REFERENCES agents (id)
);

