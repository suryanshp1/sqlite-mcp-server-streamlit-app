import sqlite3
import argparse
import nest_asyncio
from mcp.server.fastmcp import FastMCP

# Apply nest_asyncio to handle nested event loops
nest_asyncio.apply()

# Initialize the MCP server
mcp = FastMCP("Local SQLite MCP Server", port=3001)

# Database setup
DB_PATH = "/app/data/local_data.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    finally:
        conn.close()

@mcp.tool()
def add_data(query: str) -> dict:
    """
    Add data to sqlite database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        return {"success": True, "message": "Data added successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        if conn:
            conn.close()

@mcp.tool()
def fetch_data(query: str) -> dict:
    """
    Fetch data from sqlite database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return {"success": True, "data": results}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    try:
        init_db()

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--server_type", type=str, default="sse", choices=["sse", "stdio"]
        )

        args = parser.parse_args()
        mcp.run(args.server_type)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise
