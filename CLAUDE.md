# Claude Instructions for OpenShot

## Latest Backups (March 21, 2025)

- Application backup: `/root/OpenShot/test_app/backups/20250321/flux58_app_20250321_203916.tar.gz`
- Database backup: `/root/OpenShot/test_app/backups/20250321/flux58_db_20250321_204015.sql`
- PostgreSQL credentials: User `flux58_user` with password `flux58_password`
- Admin login: `admin / admin123`

### Run Application
```bash
# Using the enhanced automated launcher script (recommended)
/root/OpenShot/run_flux58.sh

# Optional: Specify a custom port
PORT=5091 /root/OpenShot/run_flux58.sh

# Manual startup (not recommended - misses library fixes)
cd /root/OpenShot/test_app
source venv/bin/activate
export LD_LIBRARY_PATH="/usr/lib:/usr/local/lib:$LD_LIBRARY_PATH"
python flux58.py
```

## Build & Test Commands (x86_64)
- Build libopenshot-audio: `cd libopenshot-audio && mkdir -p build && cd build && cmake .. -DCMAKE_INSTALL_PREFIX=/usr && make -j4`
- Install libopenshot-audio: `cd libopenshot-audio/build && sudo make install`
- Build libopenshot: `cd openshot-server && mkdir -p build && cd build && cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DUSE_SYSTEM_JSONCPP=1 && make -j4`
- Install libopenshot: `cd openshot-server/build && sudo make install`
- Run all tests: `cd openshot-server/build && make test`
- Run single test: `cd openshot-server/build && ctest -VV -L "^TestName$"` (replace TestName with actual test name like Clip)
- Generate docs: `cd openshot-server/build && make doc`
- Coverage: `cd openshot-server/build && make coverage`
- Test Python bindings: `python3 -c "import openshot; print('OpenShot Python bindings imported successfully')"`

## Code Style
- C++17 standard
- Classes use PascalCase (FrameMapper)
- Methods use PascalCase (GetFrame)
- Variables use camelCase (audioSamples)
- Constants use ALL_CAPS
- Include headers in logical groups: system, libraries, project
- Doxygen style comments with @brief, @param, @return
- Keep lines < 120 chars
- Use shared_ptr for memory management
- Error handling via exceptions (Exceptions.h)
- Format JSON with proper indentation
- Use Catch2 for unit tests

## FLUX58 Web Application (test_app)

### Service Management
- Start service: `sudo systemctl start openshot-web.service`
- Stop service: `sudo systemctl stop openshot-web.service`
- Check status: `sudo systemctl status openshot-web.service`
- View logs: `journalctl -u openshot-web.service`
- App logs: `tail -n 100 /home/juanquy/OpenShot/test_app/logs/flux58.log`

### Database Management
- Connect to PostgreSQL: `sudo -u postgres psql -d flux58`
- Backup database: `sudo -u postgres pg_dump flux58 > backup_name.sql`
- Restore database: `sudo -u postgres psql -c "DROP DATABASE IF EXISTS flux58;" && sudo -u postgres psql -c "CREATE DATABASE flux58;" && sudo -u postgres psql flux58 < backup_file.sql`

### User Accounts
- Admin user: `admin / admin123`
- Test user: `test / test123`

### Application Structure
- Main app: `/home/juanquy/OpenShot/test_app/app.py`
- Templates: `/home/juanquy/OpenShot/test_app/templates/`
- Static files: `/home/juanquy/OpenShot/test_app/static/`
- Database: `/home/juanquy/OpenShot/test_app/data/database.sqlite` (SQLite backup)
- PostgreSQL: Database name `flux58`

### Key URLs
- Admin dashboard: `http://[server-ip]:5000/admin`
- User dashboard: `http://[server-ip]:5000/dashboard`
- Login page: `http://[server-ip]:5000/login`
- Video editor: `http://[server-ip]:5000/editor?project_id=[ID]`

### Backups
- Latest application backup: `/home/juanquy/OpenShot/test_app/backups/20250319/flux58_app_20250319_010650.tar.gz`
- Latest database backup: `/home/juanquy/OpenShot/test_app/backups/20250319/flux58_db_20250319_010705.sql`
- Previous application backup: `/home/juanquy/OpenShot/backups/flux58_app_20250316_000352.tar.gz`
- Previous database backup: `/home/juanquy/OpenShot/backups/flux58_db_20250316_000432.sql`
- Backup documentation: `/home/juanquy/OpenShot/backups/README.md`

### Recent Fixes (March 22, 2025 - Latest)
- Fixed media library thumbnails not displaying in the editor UI:
  - Added proper CSS styles for media thumbnails
  - Enhanced video thumbnail loading with frame capture
  - Fixed icon and thumbnail overlap issues
  - Implemented conditional fallback icons when thumbnails unavailable
  - Added proper z-index for thumbnail elements

### Recent Fixes (March 21, 2025)
- Enhanced launcher script with OpenShot Python binding fixes
- Added advanced diagnostics for OpenShot library dependencies
- Implemented automatic pathing and environment configuration
- Created Python symlink system to fix binding issues
- Added persistent .pth file for reliable OpenShot imports
- Improved fallback mechanisms when libraries are missing
- Added clear status messages and better error handling
- Set LD_LIBRARY_PATH automatically for library loading
- Fixed Python bindings path discovery and verification
- Implemented binding integrity verification with test objects
- Successfully ported OpenShot from POWER8 (ppc64le) to x86_64 architecture
- Rebuilt all libraries and dependencies for x86_64 platform
- Fixed architecture-specific library paths and dependencies
- Set up proper build environment for x86_64
- Updated build documentation with x86_64-specific commands

### Recent Fixes (March 19, 2025)
- Improved string formatting throughout the application using .format() method
- Created flux58.py launcher script for better configuration management
- Created comprehensive backups of both code and database
- Fixed multiple format string errors throughout the application
- Enhanced application compatibility and error handling

### Recent Fixes (March 16, 2025)
- Fixed admin login with proper redirect to admin dashboard
- Enhanced session management for authentication
- Added detailed debugging for login process
- Created test user with credits for testing
- Complete database setup with PostgreSQL 
- Fixed persistent login issues with permanent secret key
- Implemented 7-day session lifetime for better user experience
- Set up persistent session management in Flask
- Created diagnostic tools for authentication troubleshooting
- Fixed project creation functionality to use correct database
- Resolved database inconsistency between app and ProjectManager
- Ensured consistent PostgreSQL usage throughout application
- Added missing project creation routes
- Implemented project details and editor pages
- Fixed foreign key constraints for project creation
- Added project deletion functionality
- Fixed "Internal Server Error" when viewing project details
- Added try/except blocks for better error handling in project routes
- Enhanced editor page with proper project loading

### Development Mode
- Run Flask with Python 3.8: `cd /home/juanquy/OpenShot/test_app && venv/bin/python3 flux58.py`
- Add test user: `cd /home/juanquy/OpenShot/test_app && python3 create_test_user.py`
- Fix database tables: `cd /home/juanquy/OpenShot/test_app && python3 create_all_tables.py`

### Project Documentation
- Main README: `/home/juanquy/OpenShot/test_app/README.md`
- Project status: `/home/juanquy/OpenShot/test_app/PROJECT_STATUS.md`
- PostgreSQL info: `/home/juanquy/OpenShot/test_app/POSTGRES.md`
- Editor UI details: `/home/juanquy/OpenShot/test_app/EDITOR_UI.md`
- AI features: `/home/juanquy/OpenShot/test_app/AI_FEATURES.md`
- Login fixes: `/home/juanquy/OpenShot/test_app/LOGIN_FIX_SUMMARY.md`
- Project creation fixes: `/home/juanquy/OpenShot/test_app/PROJECT_FIXES.md`
- Project routes fixes: `/home/juanquy/OpenShot/test_app/PROJECT_ROUTES_FIX.md`

### Enhanced Automated Launcher
The enhanced `run_flux58.sh` script now provides comprehensive OpenShot integration and environment setup:

- **Usage**: `/root/OpenShot/run_flux58.sh`
- **Custom port**: `PORT=5091 /root/OpenShot/run_flux58.sh`

**Features**:
- Automatically checks and creates Python virtual environment if missing
- Installs required dependencies from requirements.txt
- Verifies PostgreSQL connection and attempts to start the service if needed
- Provides full OpenShot Python binding integration:
  - Sets LD_LIBRARY_PATH environment variable automatically
  - Finds and links system OpenShot libraries
  - Creates symlinks to Python bindings when needed
  - Sets up persistent .pth files for reliable imports
  - Verifies OpenShot functionality with test objects
- Gracefully falls back to placeholder implementation if fixes fail
- Verifies port availability before starting (default: 5090)
- Provides clear status messages and detailed error information
- Activates the correct environment before launching flux58.py

**OpenShot Binding Fix Strategy**:
1. Sets environment variables for library loading
2. Checks multiple possible binding locations
3. Creates Python binding symlinks when needed
4. Adds persistent path configuration
5. Verifies actual OpenShot functionality
6. Uses fallback implementation when necessary

### Debugging and Maintenance Tools
- **OpenShot Library Fix**: `/root/OpenShot/test_app/fix_openshot.py` - Fixes OpenShot binding issues
- **Login debugging**: `python3 debug_login.py` - Checks authentication and user setup
- **Flask session fix**: `python3 fix_flask_sessions.py` - Fixes Flask session configuration
- **Login testing**: `python3 test_login.py` - Tests login redirection for admin and users
- **Project creation testing**: `python3 test_project_creation.py` - Tests project creation functionality
- **Project routes fix**: `python3 add_project_routes.py` - Adds missing project routes
- **Project manager fix**: `python3 fix_project_creation.py` - Fixes ProjectManager database connection

### Troubleshooting Video Editor Issues
If the video editor isn't working properly, check the following:

1. **OpenShot Library Integration**:
   ```bash
   source /root/OpenShot/test_app/venv/bin/activate
   python -c "import openshot; print(f'OpenShot version: {openshot.OPENSHOT_VERSION_FULL}')"
   ```
   If this fails, run the enhanced launcher script which automatically fixes binding issues.

2. **PostgreSQL Connection**:
   ```bash
   sudo systemctl status postgresql
   ```
   The database must be running for projects to load correctly.

3. **Library Paths**:
   ```bash
   ls -la /usr/lib/libopenshot*
   ```
   Verify that both libopenshot.so and libopenshot-audio.so are installed.

4. **Python Environment**:
   ```bash
   source /root/OpenShot/test_app/venv/bin/activate
   pip list | grep psycopg2
   ```
   Ensure the PostgreSQL connector is installed.

The enhanced launcher script will automatically detect and fix most common issues.
