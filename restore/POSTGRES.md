# Using PostgreSQL with OpenShot Web App

This document explains how to configure the OpenShot Web App to use PostgreSQL instead of SQLite.

## Latest Configuration (March 21, 2025)

The application is now configured to use PostgreSQL with the following credentials in `flux58.py`:

```python
# Database configuration (already set in flux58.py)
os.environ['DB_TYPE'] = 'postgres'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'flux58'
os.environ['DB_USER'] = 'flux58_user'
os.environ['DB_PASS'] = 'flux58_password'
```

## Prerequisites

1. PostgreSQL (version 12 or newer) installed on your system
2. Python package `psycopg2-binary` installed (included in requirements.txt):
   ```
   pip install psycopg2-binary
   ```

## Initial Setup Completed

PostgreSQL has been configured with:
- Database: `flux58`
- User: `flux58_user` 
- Password: `flux58_password`

If you need to reset or recreate this configuration:

```bash
# Install PostgreSQL if needed
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# Configure user and permissions
sudo -i -u postgres psql -c "CREATE USER flux58_user WITH PASSWORD 'flux58_password' CREATEDB;"
sudo -i -u postgres psql -c "CREATE DATABASE flux58;"
sudo -i -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE flux58 TO flux58_user;"
sudo -i -u postgres psql -d flux58 -c "GRANT ALL ON SCHEMA public TO flux58_user;"
```

## Running the Application with PostgreSQL

The environment variables are now set automatically in `flux58.py`. Simply run:

```bash
# Navigate to the application directory
cd /root/OpenShot/test_app

# Activate the virtual environment
source venv/bin/activate

# Run the application
python flux58.py
```

If port 5000 is already in use, you can specify an alternative port:

```bash
PORT=5001 python flux58.py
```

## Database Initialization

The database has been initialized with all necessary tables. If you need to recreate the database structure:

```bash
# Activate the virtual environment
cd /root/OpenShot/test_app
source venv/bin/activate

# Initialize the database
python init_postgres.py
```

This script creates all required tables, indexes, and the admin user with credentials:
- Username: `admin`
- Password: `admin123`

You can access the admin dashboard at: `http://localhost:5000/admin`

## Data Migration

If you want to migrate data from SQLite to PostgreSQL, a separate data migration script will be needed. Currently, there is no automatic migration tool provided.

## Backup and Restore

To backup your PostgreSQL database:

```bash
# Using pg_dump
pg_dump -h localhost -p 5432 -U postgres -d flux58 -f backup.sql
```

To restore from a backup:

```bash
# Using psql
psql -h localhost -p 5432 -U postgres -d flux58 -f backup.sql
```

The application also provides admin tools for database backup and restore through the web interface.

## Performance Considerations

PostgreSQL is the recommended database backend for production use:
- Multiple concurrent users with better thread safety
- Larger datasets with efficient indexing
- Complex queries with better performance
- High-traffic production environments
- Better data integrity with transaction support
- Proper datetime handling

SQLite should only be used for development or demonstration purposes due to:
- Thread safety issues in multi-threaded environments
- Limited concurrent write support
- Performance degradation with larger datasets

## Known Issues

### Thread Safety
The most significant issue when using SQLite is the "SQLite objects created in a thread can only be used in that same thread" error that occurs in multi-threaded environments.

### Data Types
PostgreSQL has native datetime support, while SQLite stores timestamps as strings. The application now properly handles datetime objects in both database backends using a unified interface.

### Connection Management
The application now properly manages database connections to avoid issues with concurrent access. Each operation opens a connection, performs the needed query, and closes the connection when finished.