# OpenShot/FLUX58 Backups

## March 16, 2025 Backups

### Latest Application Backup
- **File**: `flux58_app_20250316_044531.tar.gz`
- **Description**: Full backup of the application code with fixed admin templates.
- **Notable Changes**:
  - Fixed admin routes to use correct templates
  - Modified template references to ensure proper rendering
  - All admin interface sections now working correctly
  - OpenShot integration fully functional

### Previous Application Backup
- **File**: `flux58_app_20250316_000352.tar.gz`
- **Description**: Full backup of the working application directory with debug improvements for login and admin access.
- **Notable Changes**: 
  - Modified login handling to correctly redirect admin users to admin dashboard
  - Enhanced admin access validation
  - Added debugging to trace session management

### Latest Database Backup
- **File**: `flux58_db_20250316_044734.sql`
- **Description**: PostgreSQL database dump containing all users, projects, and system settings.

### Previous Database Backup
- **File**: `flux58_db_20250316_000432.sql`
- **Description**: PostgreSQL database dump containing all users, projects, and system settings.
- **Admin Credentials**: 
  - Username: admin
  - Password: admin123

## Restoration Instructions

### To restore the latest application:
```bash
cd /home/juanquy/OpenShot
tar -xzf backups/flux58_app_20250316_044531.tar.gz
```

### To restore the latest database:
```bash
sudo -u postgres psql -c "DROP DATABASE IF EXISTS flux58;"
sudo -u postgres psql -c "CREATE DATABASE flux58;"
sudo -u postgres psql flux58 < /home/juanquy/OpenShot/backups/flux58_db_20250316_044734.sql
```

### Alternative: Restore previous version
```bash
cd /home/juanquy/OpenShot
tar -xzf backups/flux58_app_20250316_000352.tar.gz
sudo -u postgres psql -c "DROP DATABASE IF EXISTS flux58;"
sudo -u postgres psql -c "CREATE DATABASE flux58;"
sudo -u postgres psql flux58 < /home/juanquy/OpenShot/backups/flux58_db_20250316_000432.sql
```

### To start the service:
```bash
sudo systemctl restart openshot-web.service
```