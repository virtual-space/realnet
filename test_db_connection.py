import os
from dotenv import load_dotenv
import psycopg2
import sys

# Load environment variables
load_dotenv()

# Get database connection details from environment variables
db_user = os.getenv('REALNET_DB_USER', 'postgres')
db_pass = os.getenv('REALNET_DB_PASS', 'postgres')
db_host = os.getenv('REALNET_DB_HOST', 'localhost')
db_port = os.getenv('REALNET_DB_PORT', '5432')
db_name = os.getenv('REALNET_DB_NAME', 'realnet')

print(f"Attempting to connect to PostgreSQL database:")
print(f"  Host: {db_host}")
print(f"  Port: {db_port}")
print(f"  Database: {db_name}")
print(f"  User: {db_user}")
print(f"  Password: {'*' * len(db_pass)}")

try:
    # Attempt to connect to the database
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_pass
    )
    
    # Create a cursor
    cur = conn.cursor()
    
    # Execute a simple query
    cur.execute("SELECT version();")
    
    # Fetch the result
    version = cur.fetchone()
    
    print("\nDatabase connection successful!")
    print(f"PostgreSQL version: {version[0]}")
    
    # Check if the required tables exist
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cur.fetchall()
    
    print("\nExisting tables in database:")
    if tables:
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("  No tables found. Database schema may not be initialized.")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"\nError connecting to database: {e}")
    print("\nPossible solutions:")
    print("1. Ensure PostgreSQL is installed and running")
    print("2. Verify database credentials in .env file")
    print("3. Create the 'realnet' database if it doesn't exist")
    print("4. Initialize the database schema using 'python -m realnet server initialize'")
    sys.exit(1)