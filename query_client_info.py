import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database connection parameters from environment variables
db_user = os.getenv('REALNET_DB_USER', 'postgres')
db_pass = os.getenv('REALNET_DB_PASS', 'postgres')
db_host = os.getenv('REALNET_DB_HOST', 'localhost')
db_port = os.getenv('REALNET_DB_PORT', '5432')
db_name = os.getenv('REALNET_DB_NAME', 'realnet')
db_type = os.getenv('REALNET_DB_TYPE', 'postgresql')

# Create database connection URL
db_url = f"{db_type}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

try:
    # Create database engine
    engine = create_engine(db_url)
    
    # Connect to the database
    with engine.connect() as connection:
        print("Connected to the database successfully!")
        
        # Query client information
        client_query = text("""
            SELECT c.id, c.name, c.client_id, c.client_secret, c.client_metadata, o.name as org_name
            FROM client c
            JOIN org o ON c.org_id = o.id
            ORDER BY o.name, c.name
        """)
        
        print("\nClient Information:")
        print("===================")
        
        clients = connection.execute(client_query)
        for client in clients:
            print(f"\nID: {client.id}")
            print(f"Name: {client.name}")
            print(f"Client ID: {client.client_id}")
            print(f"Client Secret: {client.client_secret}")
            print(f"Organization: {client.org_name}")
            print(f"Metadata: {client.client_metadata}")
        
        # Query available grant types
        grant_query = text("""
            SELECT DISTINCT grant_type
            FROM token
            ORDER BY grant_type
        """)
        
        print("\nAvailable Grant Types:")
        print("=====================")
        
        try:
            grants = connection.execute(grant_query)
            for grant in grants:
                print(f"- {grant.grant_type}")
        except Exception as e:
            print(f"Error querying grant types: {e}")
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)