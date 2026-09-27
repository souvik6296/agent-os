import os

import psycopg


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://agent_os:agent_os_dev@localhost:5432/agent_os",
)


def get_connection():
    """
    Create a PostgreSQL connection for Agent OS.
    """
    return psycopg.connect(DATABASE_URL)