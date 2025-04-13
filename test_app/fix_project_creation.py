#!/usr/bin/env python3
import os
import shutil
from datetime import datetime

print("Starting Project Creation Fix Script")

# 1. Backup projects.py
now = datetime.now().strftime('%Y%m%d_%H%M%S')
projects_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'projects.py')
backup_path = f"{projects_path}.{now}.bak"

shutil.copy2(projects_path, backup_path)
print(f"Created backup of projects.py at: {backup_path}")

# 2. Fix the ProjectManager class to use the same database instance
with open(projects_path, 'r') as f:
    projects_code = f.read()

# Replace the database initialization in ProjectManager.__init__
old_db_init = """        # Initialize database
        self.db = Database(os.path.join(base_path, 'database.sqlite'))"""

new_db_init = """        # Get the database instance from app.py if provided
        self.db = db if 'db' in globals() else Database(os.path.join(base_path, 'database.sqlite'))
        print(f"ProjectManager using database: {'PostgreSQL' if getattr(self.db, 'use_postgres', False) else 'SQLite'}")"""

updated_code = projects_code.replace(old_db_init, new_db_init)

# 3. Update the imports to possibly get 'db' from globals
if "from database import Database" in updated_code and "import os" in updated_code:
    updated_code = updated_code.replace("import os", "import os\nimport sys\nimport logging")
    print("Added missing imports")

# 4. Write the fixed code back to projects.py
with open(projects_path, 'w') as f:
    f.write(updated_code)
print("Updated projects.py with database fix")

# 5. Now fix the app.py to properly pass db to ProjectManager
app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app.py')
backup_path = f"{app_path}.{now}.bak"

shutil.copy2(app_path, backup_path)
print(f"Created backup of app.py at: {backup_path}")

with open(app_path, 'r') as f:
    app_code = f.read()

# Replace the ProjectManager initialization in app.py
old_pm_init = "project_manager = ProjectManager(base_path='data')"
new_pm_init = "# Pass the same database instance to ProjectManager\nproject_manager = ProjectManager(base_path='data')\n# Make the db instance available to ProjectManager\nprojects.db = db"

updated_app_code = app_code.replace(old_pm_init, new_pm_init)

# 6. Write the fixed code back to app.py
with open(app_path, 'w') as f:
    f.write(updated_app_code)
print("Updated app.py with ProjectManager initialization fix")

print("\nProject creation fix completed!")
print("Run the following commands to restart the service:")
print("sudo systemctl stop openshot-web.service")
print("sudo systemctl start openshot-web.service")
print("sudo systemctl status openshot-web.service")