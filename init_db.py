from services.db import conn

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
INSERT INTO workspaces (name, slug)
VALUES ('Default Workspace', 'default')
ON CONFLICT (slug) DO NOTHING;
""")

cursor.execute("""
SELECT workspace_id
FROM workspaces
WHERE slug='default';
""")

default_workspace = cursor.fetchone()[0]

cursor.execute("""
CREATE TABLE IF NOT EXISTS meetings (
    id SERIAL PRIMARY KEY,
    meeting_id VARCHAR(100) UNIQUE,
    title TEXT,
    created_at TIMESTAMP,
    summary TEXT,
    transcript TEXT,
    people JSONB,
    topics JSONB,
    actions JSONB,
    decisions JSONB,
    risks JSONB,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(workspace_id)
);
""")

cursor.execute("""
UPDATE meetings
SET workspace_id=%s
WHERE workspace_id IS NULL;
""", (default_workspace,))

conn.commit()

print("Database initialized successfully!")