import psycopg2
from services.db import conn


def migrate():
    cursor = conn.cursor()

    # Create workspaces table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workspaces (
            workspace_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            slug VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Check if workspace_id column exists in meetings table
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'meetings'
        AND column_name = 'workspace_id'
    """)

    column_exists = cursor.fetchone()

    if not column_exists:
        # Add workspace_id column to meetings table
        cursor.execute("""
            ALTER TABLE meetings
            ADD COLUMN workspace_id INTEGER
        """)

        # Create default workspace
        cursor.execute("""
            INSERT INTO workspaces (name, slug)
            VALUES ('Default Workspace', 'default')
            ON CONFLICT (slug) DO NOTHING
        """)

        cursor.execute("""
            SELECT workspace_id
            FROM workspaces
            WHERE slug='default'
        """)

        default_workspace_id = cursor.fetchone()[0]
        # Migrate existing meetings to default workspace
        if default_workspace_id:
            cursor.execute("""
                UPDATE meetings
                SET workspace_id = %s
                WHERE workspace_id IS NULL
            """, (default_workspace_id,))

        # Add foreign key constraint
        cursor.execute("""
            ALTER TABLE meetings
            ADD CONSTRAINT fk_workspace
            FOREIGN KEY (workspace_id)
            REFERENCES workspaces(workspace_id)
        """)

        # Make workspace_id NOT NULL
        cursor.execute("""
            ALTER TABLE meetings
            ALTER COLUMN workspace_id SET NOT NULL
        """)

    conn.commit()
    print("Migration completed successfully.")


if __name__ == "__main__":
    migrate()
