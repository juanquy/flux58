# Project Creation Fix - FLUX58 Web Application

## Problem Summary
Creating a new project resulted in an "Internal Server Error" when clicking the "Create Project" button. The specific URL was `/projects/new` when the error occurred. This prevented users from creating new video projects in the application.

## Root Cause
The root cause was a database connection inconsistency between the main application and the `ProjectManager` class:

1. The main application (`app.py`) was correctly configured to use PostgreSQL:
   ```python
   db = Database(use_postgres=True, host=DB_HOST, port=DB_PORT, 
                database=DB_NAME, user=DB_USER, password=DB_PASS)
   ```

2. However, the `ProjectManager` class (`projects.py`) was initializing its own separate Database instance using SQLite:
   ```python
   def __init__(self, base_path='data'):
       # ...
       # Initialize database
       self.db = Database(os.path.join(base_path, 'database.sqlite'))
   ```

3. This resulted in:
   - The main application creating users, sessions, etc. in PostgreSQL
   - The ProjectManager trying to create projects in SQLite
   - When clicking "Create Project", an error occurred because:
     - The user existed in PostgreSQL
     - The ProjectManager tried to create a project in SQLite
     - It couldn't find the user in SQLite, resulting in a foreign key constraint failure

## Solution

### 1. Modified the ProjectManager class to use the existing database connection
```python
# Get the database instance from app.py if provided
self.db = db if 'db' in globals() else Database(os.path.join(base_path, 'database.sqlite'))
print(f"ProjectManager using database: {'PostgreSQL' if getattr(self.db, 'use_postgres', False) else 'SQLite'}")
```

### 2. Updated app.py to share its database connection with ProjectManager
```python
# Pass the same database instance to ProjectManager
project_manager = ProjectManager(base_path='data')
# Make the db instance available to ProjectManager
projects.db = db
```

This ensures:
1. Both the main application and ProjectManager use the same database connection
2. All database operations (user authentication, project creation, etc.) are performed against the same PostgreSQL database
3. Foreign key relationships between users and projects are properly maintained

## Implementation Details

1. Created a backup of both files before making changes
2. Added appropriate imports in projects.py
3. Modified the initialization logic to check for an existing db instance
4. Updated app.py to share its db instance with the projects module
5. Restarted the service to apply changes

## Testing
After applying the fix and restarting the service, users can:
1. Log in as normal
2. Navigate to the project creation page
3. Enter project details
4. Click "Create Project" successfully
5. Be redirected to the new project editor

## Preventive Measures

1. **Consistent Database Usage**: Ensure all components use the same database connection instance
2. **Dependency Injection**: Pass critical services like database connections to components rather than having them create their own
3. **Error Logging**: Improve error logging to catch similar issues more quickly

## Future Improvements

1. **Service Pattern**: Consider refactoring to use a service pattern where database and other core services are initialized once and injected into components
2. **Configuration Management**: Centralize configuration values to ensure consistency
3. **Error Handling**: Add more comprehensive error handling and user-friendly error messages