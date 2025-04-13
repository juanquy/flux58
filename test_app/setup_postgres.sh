#!/bin/bash
# Setup PostgreSQL database for OpenShot Web App

# Set variables
DB_NAME="flux58"
DB_USER="postgres"
DB_PASS="postgres"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Please install it first."
    exit 1
fi

# Connect to PostgreSQL and create database if it doesn't exist
sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1
if [ $? -ne 0 ]; then
    echo "Creating database $DB_NAME"
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;"
    echo "Database created successfully"
else
    echo "Database $DB_NAME already exists"
fi

# Install psycopg2 if not already installed
pip install psycopg2-binary

# Run the Python initialization script to create tables
python init_postgres.py

echo "PostgreSQL setup completed"