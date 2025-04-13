#!/usr/bin/env python3
import os
import sys
import psycopg2

# Set up environment
os.environ['DB_TYPE'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'flux58'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASS'] = 'postgres'

# Import our custom modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'flux58'
DB_USER = 'postgres'
DB_PASS = 'postgres'

# Connect directly to PostgreSQL
try:
    # Connect to database
    logger.info(f"Connecting to database: {DB_NAME} on {DB_HOST}:{DB_PORT}")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create assets table if it doesn't exist
    assets_table_query = """
    CREATE TABLE IF NOT EXISTS assets (
        id VARCHAR(50) PRIMARY KEY,
        project_id VARCHAR(50) NOT NULL,
        name VARCHAR(255) NOT NULL,
        type VARCHAR(50) NOT NULL,
        file_extension VARCHAR(20) NOT NULL,
        file_path VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    );
    """
    
    # Create exports table if it doesn't exist
    exports_table_query = """
    CREATE TABLE IF NOT EXISTS exports (
        id VARCHAR(50) PRIMARY KEY,
        project_id VARCHAR(50) NOT NULL,
        user_id VARCHAR(50) NOT NULL,
        format VARCHAR(20) NOT NULL,
        resolution VARCHAR(50) NOT NULL,
        status VARCHAR(20) NOT NULL,
        progress INTEGER NOT NULL,
        file_path VARCHAR(255) NOT NULL,
        created_at TIMESTAMP NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    
    # Execute the queries
    cursor.execute(assets_table_query)
    logger.info("Assets table created or already exists")
    
    cursor.execute(exports_table_query)
    logger.info("Exports table created or already exists")
    
    # Close the connection
    cursor.close()
    conn.close()
    
    logger.info("Database update complete!")
    
except Exception as e:
    logger.error(f"Error updating database: {str(e)}")
    sys.exit(1)