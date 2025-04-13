#!/usr/bin/env python3
"""
FLUX58 AI MEDIA LABS - Consolidated Application
A web application for video editing with OpenShot integration
"""

import os
import sys
import json
import uuid
import logging
from datetime import datetime, timedelta
import threading
from logging.handlers import RotatingFileHandler
import shutil
from werkzeug.security import generate_password_hash, check_password_hash

# Get the absolute path to the script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROJECTS_DIR = os.path.join(DATA_DIR, 'projects')
EXPORTS_DIR = os.path.join(DATA_DIR, 'exports')
UPLOADS_DIR = os.path.join(DATA_DIR, 'uploads')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
BACKUPS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'backups')

# Create necessary directories if they don't exist
for directory in [DATA_DIR, PROJECTS_DIR, EXPORTS_DIR, UPLOADS_DIR, LOGS_DIR, BACKUPS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Database configuration with environment variable fallbacks
DB_TYPE = os.environ.get('DB_TYPE', 'postgres')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '5432'))
DB_NAME = os.environ.get('DB_NAME', 'flux58')
DB_USER = os.environ.get('DB_USER', 'flux58_user')
DB_PASS = os.environ.get('DB_PASS', 'flux58_password')

# Flask configuration
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
if not FLASK_SECRET_KEY:
    # Try to read from file
    secret_key_path = os.path.join(BASE_DIR, '.flask_secret_key')
    try:
        if os.path.exists(secret_key_path):
            with open(secret_key_path, 'r') as f:
                FLASK_SECRET_KEY = f.read().strip()
    except Exception:
        pass
        
    # Generate if still missing
    if not FLASK_SECRET_KEY:
        import secrets
        FLASK_SECRET_KEY = secrets.token_hex(32)
        
        # Try to save for future use
        try:
            with open(secret_key_path, 'w') as f:
                f.write(FLASK_SECRET_KEY)
        except Exception:
            logging.warning("Could not save Flask secret key to file")

# Application settings
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
EXPORT_CONCURRENT_JOBS = int(os.environ.get('EXPORT_CONCURRENT_JOBS', '2'))

#----------------------------------------------------------
# Logging System
#----------------------------------------------------------

# Global logger instance
app_logger = None
db = None

# Log levels
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"

# Thread-local storage for request context
_thread_local = threading.local()

def set_request_context(user_id=None, ip_address=None):
    """Set user information for the current request/thread"""
    _thread_local.user_id = user_id
    _thread_local.ip_address = ip_address

def get_request_context():
    """Get user information for the current request/thread"""
    user_id = getattr(_thread_local, 'user_id', None)
    ip_address = getattr(_thread_local, 'ip_address', None)
    return user_id, ip_address

def clear_request_context():
    """Clear user information for the current request/thread"""
    if hasattr(_thread_local, 'user_id'):
        del _thread_local.user_id
    if hasattr(_thread_local, 'ip_address'):
        del _thread_local.ip_address

def init_logger(database=None, log_dir='logs', log_level=logging.INFO):
    """Initialize the logging system"""
    global app_logger, db
    
    if app_logger is not None:
        return app_logger
    
    # Store database instance for database logging
    db = database
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure Python's logging system
    app_logger = logging.getLogger('flux58')
    app_logger.setLevel(log_level)
    
    # Format for log messages
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    app_logger.addHandler(console_handler)
    
    # File handler (rotating, max 10MB, keep 10 backup files)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'flux58.log'),
        maxBytes=10*1024*1024,
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    app_logger.addHandler(file_handler)
    
    # Don't propagate to root logger
    app_logger.propagate = False
    
    return app_logger

def _log_to_database(level, module, message):
    """Log message to database if database is available"""
    if db is None:
        return
    
    try:
        # Get request context
        user_id, ip_address = get_request_context()
        
        # Log to database using PostgreSQL
        db.add_log(level, module, message, user_id, ip_address)
    except Exception as e:
        # If database logging fails, at least log to file
        if app_logger:
            app_logger.error(f"Failed to log to database: {str(e)}")

def debug(message, module=None):
    """Log a debug message"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if app_logger:
        app_logger.debug(message)
    
    # Debug messages are typically not logged to DB to avoid filling it up

def info(message, module=None):
    """Log an info message"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if app_logger:
        app_logger.info(message)
    
    _log_to_database(INFO, module, message)

def warning(message, module=None):
    """Log a warning message"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if app_logger:
        app_logger.warning(message)
    
    _log_to_database(WARNING, module, message)

def error(message, module=None, exc_info=None):
    """Log an error message"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if exc_info:
        if app_logger:
            app_logger.error(message, exc_info=True)
        
        # Add exception details to database log
        tb = traceback.format_exc()
        full_message = f"{message}\n{tb}"
        _log_to_database(ERROR, module, full_message)
    else:
        if app_logger:
            app_logger.error(message)
        
        _log_to_database(ERROR, module, message)

def critical(message, module=None, exc_info=None):
    """Log a critical message"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if exc_info:
        if app_logger:
            app_logger.critical(message, exc_info=True)
        
        # Add exception details to database log
        tb = traceback.format_exc()
        full_message = f"{message}\n{tb}"
        _log_to_database(CRITICAL, module, full_message)
    else:
        if app_logger:
            app_logger.critical(message)
        
        _log_to_database(CRITICAL, module, message)

def exception(message, module=None):
    """Log an exception message (includes traceback)"""
    if not module:
        # Get calling module name
        frame = sys._getframe(1)
        module = frame.f_globals['__name__']
    
    if app_logger:
        app_logger.exception(message)
    
    # Format exception info for database
    tb = traceback.format_exc()
    full_message = f"{message}\n{tb}"
    _log_to_database(ERROR, module, full_message)

def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        module = func.__module__
        
        info(f"Function {func_name} called", module)
        
        try:
            result = func(*args, **kwargs)
            debug(f"Function {func_name} completed successfully", module)
            return result
        except Exception as e:
            error(f"Function {func_name} failed: {str(e)}", module, exc_info=True)
            raise
    
    return wrapper

#----------------------------------------------------------
# Database System
#----------------------------------------------------------

# Thread-local storage for database connections
_db_thread_local = threading.local()

class PostgresDatabase:
    def __init__(self, 
                host='localhost', 
                port=5432, 
                database='flux58',
                user='postgres', 
                password='postgres'):
        """Initialize the PostgreSQL database connection parameters"""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.db_params = {
            'host': host, 
            'port': port, 
            'database': database, 
            'user': user, 
            'password': password
        }
        
        # Initialize the database schema
        self._initialize_db()
    
    def _get_connection(self):
        """Get a thread-local database connection"""
        try:
            import psycopg2
            import psycopg2.extras
            
            # Check if this thread already has a connection
            if not hasattr(_db_thread_local, 'pg_connection'):
                # Create a new connection for this thread
                _db_thread_local.pg_connection = psycopg2.connect(**self.db_params)
                # Enable automatic commit on close
                _db_thread_local.pg_connection.autocommit = False
                # Use RealDictCursor to return query results as dictionaries
                _db_thread_local.pg_cursor = _db_thread_local.pg_connection.cursor(
                    cursor_factory=psycopg2.extras.RealDictCursor
                )
            
            return _db_thread_local.pg_connection, _db_thread_local.pg_cursor
        except ImportError:
            logging.error("psycopg2 module not found. Please install with 'pip install psycopg2-binary'")
            raise
        except Exception as e:
            logging.error(f"Error connecting to PostgreSQL: {str(e)}")
            raise
    
    def _close_connection(self, commit=True):
        """Close the thread-local database connection"""
        if hasattr(_db_thread_local, 'pg_connection'):
            if commit:
                _db_thread_local.pg_connection.commit()
            _db_thread_local.pg_cursor.close()
            _db_thread_local.pg_connection.close()
            del _db_thread_local.pg_cursor
            del _db_thread_local.pg_connection
    
    def _execute_query(self, query, params=None, fetch=True, commit=True):
        """Execute a SQL query and optionally fetch results"""
        try:
            conn, cursor = self._get_connection()
            
            # Execute the query
            cursor.execute(query, params or ())
            
            result = None
            if fetch:
                # Only fetch if the command is a SELECT or other query that returns results
                if query.strip().upper().startswith(('SELECT', 'SHOW', 'EXPLAIN', 'DESCRIBE')):
                    result = cursor.fetchall()
            
            if commit:
                conn.commit()
            
            return result
        except Exception as e:
            conn, _ = self._get_connection()
            conn.rollback()
            logging.error(f"Database error: {str(e)}")
            logging.error(f"Failed query: {query}")
            if params:
                logging.error(f"Parameters: {params}")
            raise
    
    def _initialize_db(self):
        """Initialize database tables if they don't exist"""
        try:
            import psycopg2
            
            # Test connection to see if database exists
            try:
                conn, _ = self._get_connection()
                # Database exists, we can proceed with initialization
                self._close_connection(commit=False)
            except psycopg2.OperationalError as e:
                if "does not exist" in str(e):
                    # Database doesn't exist, we need to create it
                    # Connect to default 'postgres' database to create our database
                    temp_params = self.db_params.copy()
                    temp_params['database'] = 'postgres'
                    
                    conn = psycopg2.connect(**temp_params)
                    conn.autocommit = True
                    cursor = conn.cursor()
                    
                    # Create database
                    cursor.execute(f"CREATE DATABASE {self.database}")
                    
                    # Close connection to postgres database
                    cursor.close()
                    conn.close()
                else:
                    # Some other error occurred
                    raise
            
            # Now create tables
            # Users table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL,
                role VARCHAR(50) NOT NULL
            )
            ''')
            
            # Sessions table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS sessions (
                token VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                username VARCHAR(100) NOT NULL,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                ip_address VARCHAR(50),
                user_agent TEXT,
                last_activity TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')
            
            # Create index on expires_at
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)
            ''')
            
            # Create index on user_id
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)
            ''')
            
            # Credits table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS credits (
                user_id VARCHAR(36) PRIMARY KEY,
                total INTEGER NOT NULL,
                used INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')
            
            # Credit transactions table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS credit_transactions (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                amount INTEGER NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                type VARCHAR(50) NOT NULL,
                description TEXT,
                status VARCHAR(50) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')
            
            # Create index on user_id and timestamp
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_transactions_user_timestamp 
            ON credit_transactions(user_id, timestamp DESC)
            ''')
            
            # Projects table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS projects (
                id VARCHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                user_id VARCHAR(36) NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')
            
            # Create index on user_id and updated_at
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_projects_user_updated 
            ON projects(user_id, updated_at DESC)
            ''')
            
            # Project assets table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS project_assets (
                id VARCHAR(36) PRIMARY KEY,
                project_id VARCHAR(36) NOT NULL,
                name VARCHAR(255) NOT NULL,
                filename VARCHAR(255) NOT NULL,
                path TEXT NOT NULL,
                type VARCHAR(50) NOT NULL,
                added_at TIMESTAMP NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            ''')
            
            # Create index on project_id
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_assets_project_id 
            ON project_assets(project_id)
            ''')
            
            # Create index on type
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_assets_type 
            ON project_assets(type)
            ''')
            
            # Project timeline table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS project_timeline (
                project_id VARCHAR(36) PRIMARY KEY,
                duration REAL NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                fps_num INTEGER NOT NULL,
                fps_den INTEGER NOT NULL,
                sample_rate INTEGER NOT NULL,
                channels INTEGER NOT NULL,
                channel_layout INTEGER NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            ''')
            
            # Timeline tracks table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS timeline_tracks (
                id VARCHAR(36) PRIMARY KEY,
                project_id VARCHAR(36) NOT NULL,
                name VARCHAR(255) NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
            ''')
            
            # Create index on project_id
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_tracks_project_id 
            ON timeline_tracks(project_id)
            ''')
            
            # Timeline clips table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS timeline_clips (
                id VARCHAR(36) PRIMARY KEY,
                track_id VARCHAR(36) NOT NULL,
                asset_id VARCHAR(36) NOT NULL,
                position REAL NOT NULL,
                duration REAL NOT NULL,
                start_point REAL NOT NULL,
                end_point REAL NOT NULL,
                properties JSONB NOT NULL,
                FOREIGN KEY (track_id) REFERENCES timeline_tracks(id) ON DELETE CASCADE,
                FOREIGN KEY (asset_id) REFERENCES project_assets(id) ON DELETE CASCADE
            )
            ''')
            
            # Create index on track_id
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_clips_track_id 
            ON timeline_clips(track_id)
            ''')
            
            # Create index on asset_id
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_clips_asset_id 
            ON timeline_clips(asset_id)
            ''')
            
            # Export jobs table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS export_jobs (
                id VARCHAR(36) PRIMARY KEY,
                project_id VARCHAR(36) NOT NULL,
                user_id VARCHAR(36) NOT NULL,
                output_path TEXT NOT NULL,
                format VARCHAR(20) NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                fps INTEGER NOT NULL,
                video_bitrate VARCHAR(50) NOT NULL,
                audio_bitrate VARCHAR(50) NOT NULL,
                start_frame INTEGER NOT NULL,
                end_frame INTEGER,
                started_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP,
                status VARCHAR(50) NOT NULL,
                priority INTEGER DEFAULT 0,
                progress REAL DEFAULT 0,
                error TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')
            
            # Create index on user_id and started_at
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_exports_user_started 
            ON export_jobs(user_id, started_at DESC)
            ''')
            
            # Create index on status
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_exports_status 
            ON export_jobs(status)
            ''')
            
            # Create index on priority
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_exports_priority 
            ON export_jobs(priority DESC)
            ''')
            
            # System settings table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS system_settings (
                key VARCHAR(100) PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
            ''')
            
            # System logs table
            self._execute_query('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                level VARCHAR(20) NOT NULL,
                module VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                user_id VARCHAR(36),
                ip_address VARCHAR(50),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            ''')
            
            # Create index on timestamp
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
            ON system_logs(timestamp DESC)
            ''')
            
            # Create index on level
            self._execute_query('''
            CREATE INDEX IF NOT EXISTS idx_logs_level 
            ON system_logs(level)
            ''')
            
            self._close_connection()
            
            logging.info("PostgreSQL database initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing database: {str(e)}")
            raise
    
    # User Management Methods
    def create_user(self, user_id, username, password_hash, email, role="user"):
        """Create a new user"""
        try:
            now = datetime.now()
            
            # Insert user
            self._execute_query(
                """INSERT INTO users 
                   (id, username, password_hash, email, created_at, role) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, username, password_hash, email, now, role),
                fetch=False
            )
            
            # Initialize credits
            self._execute_query(
                "INSERT INTO credits (user_id, total, used) VALUES (%s, %s, %s)",
                (user_id, 0, 0),
                fetch=False
            )
            
            return True
        except Exception as e:
            logging.error(f"Error creating user: {str(e)}")
            return False
    
    def get_user_by_username(self, username):
        """Get user by username"""
        try:
            result = self._execute_query(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
        except Exception as e:
            logging.error(f"Error getting user by username: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            result = self._execute_query(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
        except Exception as e:
            logging.error(f"Error getting user by ID: {str(e)}")
            return None
    
    def update_user(self, user_id, email=None, password_hash=None, role=None):
        """Update user details"""
        try:
            update_parts = []
            params = []
            
            if email:
                update_parts.append("email = %s")
                params.append(email)
            
            if password_hash:
                update_parts.append("password_hash = %s")
                params.append(password_hash)
            
            if role:
                update_parts.append("role = %s")
                params.append(role)
            
            if not update_parts:
                return False
            
            # Add user_id to params
            params.append(user_id)
            
            # Execute update
            query = f"UPDATE users SET {', '.join(update_parts)} WHERE id = %s"
            
            result = self._execute_query(query, params, fetch=False)
            
            return True
        except Exception as e:
            logging.error(f"Error updating user: {str(e)}")
            return False
    
    def delete_user(self, user_id):
        """Delete user"""
        try:
            self._execute_query(
                "DELETE FROM users WHERE id = %s",
                (user_id,),
                fetch=False
            )
            
            return True
        except Exception as e:
            logging.error(f"Error deleting user: {str(e)}")
            return False
    
    def list_all_users(self):
        """List all users"""
        try:
            result = self._execute_query("SELECT * FROM users")
            
            return [dict(row) for row in result]
        except Exception as e:
            logging.error(f"Error listing users: {str(e)}")
            return []
    
    # Session Management Methods
    def create_session(self, token, user_id, username, expires_at):
        """Create a new session"""
        try:
            now = datetime.now()
            
            self._execute_query(
                """INSERT INTO sessions 
                   (token, user_id, username, created_at, expires_at) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (token, user_id, username, now, expires_at),
                fetch=False
            )
            
            return True
        except Exception as e:
            logging.error(f"Error creating session: {str(e)}")
            return False
    
    def create_session_extended(self, token, user_id, username, expires_at, ip_address=None, user_agent=None):
        """Create a new session with extended information"""
        try:
            now = datetime.now()
            
            self._execute_query(
                """INSERT INTO sessions 
                   (token, user_id, username, created_at, expires_at, ip_address, user_agent, last_activity) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (token, user_id, username, now, expires_at, ip_address, user_agent, now),
                fetch=False
            )
            
            return True
        except Exception as e:
            logging.error(f"Error creating extended session: {str(e)}")
            return False
    
    def get_session(self, token):
        """Get session by token"""
        try:
            result = self._execute_query(
                "SELECT * FROM sessions WHERE token = %s",
                (token,)
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
        except Exception as e:
            logging.error(f"Error getting session: {str(e)}")
            return None
    
    def update_session_activity(self, token, ip_address=None):
        """Update session last activity time"""
        try:
            now = datetime.now()
            
            if ip_address:
                self._execute_query(
                    "UPDATE sessions SET last_activity = %s, ip_address = %s WHERE token = %s",
                    (now, ip_address, token),
                    fetch=False
                )
            else:
                self._execute_query(
                    "UPDATE sessions SET last_activity = %s WHERE token = %s",
                    (now, token),
                    fetch=False
                )
            
            return True
        except Exception as e:
            logging.error(f"Error updating session activity: {str(e)}")
            return False
    
    def delete_session(self, token):
        """Delete session"""
        try:
            self._execute_query(
                "DELETE FROM sessions WHERE token = %s",
                (token,),
                fetch=False
            )
            
            return True
        except Exception as e:
            logging.error(f"Error deleting session: {str(e)}")
            return False
    
    def cleanup_expired_sessions(self):
        """Delete expired sessions"""
        try:
            now = datetime.now()
            
            result = self._execute_query(
                "DELETE FROM sessions WHERE expires_at < %s",
                (now,),
                fetch=False
            )
            
            # In PostgreSQL, we would use cursor.rowcount to get the number of affected rows
            conn, cursor = self._get_connection()
            return cursor.rowcount
        except Exception as e:
            logging.error(f"Error cleaning up sessions: {str(e)}")
            return 0
    
    def get_user_sessions(self, user_id):
        """Get all active sessions for a user"""
        try:
            now = datetime.now()
            
            result = self._execute_query(
                "SELECT * FROM sessions WHERE user_id = %s AND expires_at > %s ORDER BY last_activity DESC",
                (user_id, now)
            )
            
            return [dict(row) for row in result]
        except Exception as e:
            logging.error(f"Error getting user sessions: {str(e)}")
            return []
    
    def invalidate_all_user_sessions(self, user_id, except_token=None):
        """Invalidate all sessions for a user except the current one"""
        try:
            if except_token:
                self._execute_query(
                    "DELETE FROM sessions WHERE user_id = %s AND token != %s",
                    (user_id, except_token),
                    fetch=False
                )
            else:
                self._execute_query(
                    "DELETE FROM sessions WHERE user_id = %s",
                    (user_id,),
                    fetch=False
                )
            
            # Get number of affected rows
            conn, cursor = self._get_connection()
            return cursor.rowcount
        except Exception as e:
            logging.error(f"Error invalidating sessions: {str(e)}")
            return 0
    
    # Credit Management Methods
    def get_user_credits(self, user_id):
        """Get user's credit information"""
        try:
            # Get credit balance
            credit_result = self._execute_query(
                "SELECT * FROM credits WHERE user_id = %s",
                (user_id,)
            )
            
            if not credit_result or len(credit_result) == 0:
                return None
            
            credit_data = dict(credit_result[0])
            
            # Get recent transactions
            tx_result = self._execute_query(
                """SELECT * FROM credit_transactions 
                   WHERE user_id = %s 
                   ORDER BY timestamp DESC 
                   LIMIT 20""",
                (user_id,)
            )
            
            credit_data['transactions'] = [dict(row) for row in tx_result]
            
            return credit_data
        except Exception as e:
            logging.error(f"Error getting user credits: {str(e)}")
            return None
    
    def add_credits(self, user_id, amount, transaction_type, description="", status="completed"):
        """Add credits to user account"""
        if amount <= 0:
            return False
        
        try:
            conn, _ = self._get_connection()
            
            # Start transaction
            conn.autocommit = False
            
            # Update credit balance
            self._execute_query(
                "UPDATE credits SET total = total + %s WHERE user_id = %s",
                (amount, user_id),
                fetch=False,
                commit=False
            )
            
            # Get number of affected rows
            conn, cursor = self._get_connection()
            if cursor.rowcount == 0:
                # Insert new record if doesn't exist
                self._execute_query(
                    "INSERT INTO credits (user_id, total, used) VALUES (%s, %s, %s)",
                    (user_id, amount, 0),
                    fetch=False,
                    commit=False
                )
            
            # Add transaction record
            transaction_id = str(uuid.uuid4())
            now = datetime.now()
            
            self._execute_query(
                """INSERT INTO credit_transactions 
                   (id, user_id, amount, timestamp, type, description, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (transaction_id, user_id, amount, now, transaction_type, description, status),
                fetch=False,
                commit=False
            )
            
            # Commit transaction
            conn.commit()
            
            return transaction_id
        except Exception as e:
            logging.error(f"Error adding credits: {str(e)}")
            conn, _ = self._get_connection()
            conn.rollback()
            return False
        finally:
            conn, _ = self._get_connection()
            conn.autocommit = True
    
    def use_credits(self, user_id, amount, description="", transaction_type="usage", status="completed"):
        """Use credits from user account"""
        if amount <= 0:
            return False
        
        try:
            conn, _ = self._get_connection()
            
            # Start transaction
            conn.autocommit = False
            
            # Check current balance
            balance_result = self._execute_query(
                "SELECT total, used FROM credits WHERE user_id = %s",
                (user_id,),
                commit=False
            )
            
            if not balance_result or len(balance_result) == 0:
                conn.rollback()
                return False
            
            row = balance_result[0]
            available = row['total'] - row['used']
            
            if available < amount:
                conn.rollback()
                return False
            
            # Update used credits
            self._execute_query(
                "UPDATE credits SET used = used + %s WHERE user_id = %s",
                (amount, user_id),
                fetch=False,
                commit=False
            )
            
            # Add transaction record (negative amount for usage)
            transaction_id = str(uuid.uuid4())
            now = datetime.now()
            
            self._execute_query(
                """INSERT INTO credit_transactions 
                   (id, user_id, amount, timestamp, type, description, status) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (transaction_id, user_id, -amount, now, transaction_type, description, status),
                fetch=False,
                commit=False
            )
            
            # Commit transaction
            conn.commit()
            
            return transaction_id
        except Exception as e:
            logging.error(f"Error using credits: {str(e)}")
            conn, _ = self._get_connection()
            conn.rollback()
            return False
        finally:
            conn, _ = self._get_connection()
            conn.autocommit = True
    
    # Project Management Methods
    def create_project(self, project_id, user_id, name, description=""):
        """Create a new project"""
        try:
            now = datetime.now()
            
            # Start transaction
            conn, _ = self._get_connection()
            conn.autocommit = False
            
            # Add project
            self._execute_query(
                """INSERT INTO projects 
                   (id, name, description, user_id, created_at, updated_at) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (project_id, name, description, user_id, now, now),
                fetch=False,
                commit=False
            )
            
            # Add timeline defaults
            self._execute_query(
                """INSERT INTO project_timeline 
                   (project_id, duration, width, height, fps_num, fps_den, 
                    sample_rate, channels, channel_layout) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (project_id, 60.0, 1920, 1080, 30, 1, 48000, 2, 3),
                fetch=False,
                commit=False
            )
            
            # Commit transaction
            conn.commit()
            
            # Return full project data
            return self.get_project(project_id)
        except Exception as e:
            logging.error(f"Error creating project: {str(e)}")
            conn, _ = self._get_connection()
            conn.rollback()
            return None
        finally:
            conn, _ = self._get_connection()
            conn.autocommit = True
    
    def get_project(self, project_id):
        """Get project by ID including all related data"""
        try:
            # Get project
            project_result = self._execute_query(
                "SELECT * FROM projects WHERE id = %s",
                (project_id,)
            )
            
            if not project_result or len(project_result) == 0:
                return None
            
            project = dict(project_result[0])
            
            # Get timeline
            timeline_result = self._execute_query(
                "SELECT * FROM project_timeline WHERE project_id = %s",
                (project_id,)
            )
            
            if not timeline_result or len(timeline_result) == 0:
                # Create default timeline
                timeline = {
                    "duration": 60.0,
                    "width": 1920,
                    "height": 1080,
                    "fps": {
                        "num": 30,
                        "den": 1
                    },
                    "sample_rate": 48000,
                    "channels": 2,
                    "channel_layout": 3,
                    "tracks": []
                }
            else:
                timeline_row = timeline_result[0]
                timeline = {
                    "duration": timeline_row['duration'],
                    "width": timeline_row['width'],
                    "height": timeline_row['height'],
                    "fps": {
                        "num": timeline_row['fps_num'],
                        "den": timeline_row['fps_den']
                    },
                    "sample_rate": timeline_row['sample_rate'],
                    "channels": timeline_row['channels'],
                    "channel_layout": timeline_row['channel_layout'],
                    "tracks": []
                }
            
            # Get tracks
            track_result = self._execute_query(
                "SELECT * FROM timeline_tracks WHERE project_id = %s",
                (project_id,)
            )
            
            tracks = []
            for track_row in track_result:
                track = dict(track_row)
                
                # Get clips for this track
                clip_result = self._execute_query(
                    "SELECT * FROM timeline_clips WHERE track_id = %s",
                    (track['id'],)
                )
                
                clips = []
                for clip_row in clip_result:
                    clip = dict(clip_row)
                    # Convert JSON properties to dict
                    clip['properties'] = clip['properties']
                    # Rename start_point and end_point to match the expected API
                    clip['start'] = clip.pop('start_point', 0)
                    clip['end'] = clip.pop('end_point', 0)
                    clips.append(clip)
                
                track['clips'] = clips
                tracks.append(track)
            
            timeline['tracks'] = tracks
            
            # Get assets
            asset_result = self._execute_query(
                "SELECT * FROM project_assets WHERE project_id = %s",
                (project_id,)
            )
            
            assets = [dict(row) for row in asset_result]
            
            # Compose final project object
            project['timeline'] = timeline
            project['assets'] = assets
            
            return project
        except Exception as e:
            logging.error(f"Error getting project: {str(e)}")
            return None
    
    def update_project(self, project_id, name=None, description=None):
        """Update project metadata"""
        try:
            update_parts = []
            params = []
            
            if name:
                update_parts.append("name = %s")
                params.append(name)
            
            if description is not None:  # Allow empty description
                update_parts.append("description = %s")
                params.append(description)
            
            if not update_parts:
                return False
            
            # Always update timestamp
            update_parts.append("updated_at = %s")
            now = datetime.now()
            params.append(now)
            
            # Add project_id to params
            params.append(project_id)
            
            # Execute update
            query = f"UPDATE projects SET {', '.join(update_parts)} WHERE id = %s"
            self._execute_query(query, params, fetch=False)
            
            return True
        except Exception as e:
            logging.error(f"Error updating project: {str(e)}")
            return False
    
    def delete_project(self, project_id):
        """Delete project and all related data"""
        try:
            # PostgreSQL will cascade delete all related data
            self._execute_query(
                "DELETE FROM projects WHERE id = %s",
                (project_id,),
                fetch=False
            )
            
            # Get number of affected rows
            conn, cursor = self._get_connection()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error deleting project: {str(e)}")
            return False
    
    def list_user_projects(self, user_id):
        """List projects for a user"""
        try:
            result = self._execute_query(
                "SELECT * FROM projects WHERE user_id = %s ORDER BY updated_at DESC",
                (user_id,)
            )
            
            return [dict(row) for row in result]
        except Exception as e:
            logging.error(f"Error listing user projects: {str(e)}")
            return []

    # Asset Management Methods
    def add_asset(self, asset_id, project_id, name, filename, path, asset_type):
        """Add an asset to a project"""
        try:
            now = datetime.now()
            
            self._execute_query(
                """INSERT INTO project_assets
                   (id, project_id, name, filename, path, type, added_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (asset_id, project_id, name, filename, path, asset_type, now),
                fetch=False
            )
            
            result = self._execute_query(
                "SELECT * FROM project_assets WHERE id = %s",
                (asset_id,)
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
        except Exception as e:
            logging.error(f"Error adding asset: {str(e)}")
            return None
    
    def get_asset(self, asset_id):
        """Get asset by ID"""
        try:
            result = self._execute_query(
                "SELECT * FROM project_assets WHERE id = %s",
                (asset_id,)
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
        except Exception as e:
            logging.error(f"Error getting asset: {str(e)}")
            return None
    
    # Timeline Management Methods
    def add_track(self, track_id, project_id, name):
        """Add a track to a project timeline"""
        try:
            self._execute_query(
                "INSERT INTO timeline_tracks (id, project_id, name) VALUES (%s, %s, %s)",
                (track_id, project_id, name),
                fetch=False
            )
            
            result = self._execute_query(
                "SELECT * FROM timeline_tracks WHERE id = %s",
                (track_id,)
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
        except Exception as e:
            logging.error(f"Error adding track: {str(e)}")
            return None
    
    def add_clip(self, clip_id, track_id, asset_id, position, duration, start=0, end=None, properties=None):
        """Add a clip to a timeline track"""
        try:
            if end is None:
                end = duration
                
            if properties is None:
                properties = {
                    "volume": 1.0,
                    "position_x": 0,
                    "position_y": 0,
                    "scale_x": 1.0,
                    "scale_y": 1.0,
                    "rotation": 0,
                    "alpha": 1.0
                }
            
            # Convert properties to JSON
            properties_json = json.dumps(properties)
            
            self._execute_query(
                """INSERT INTO timeline_clips
                   (id, track_id, asset_id, position, duration, start_point, end_point, properties)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)""",
                (clip_id, track_id, asset_id, position, duration, start, end, properties_json),
                fetch=False
            )
            
            result = self._execute_query(
                "SELECT * FROM timeline_clips WHERE id = %s",
                (clip_id,)
            )
            
            if result and len(result) > 0:
                clip = dict(result[0])
                # Convert JSON string back to dict
                clip['properties'] = clip['properties']
                # Rename fields to match expected API
                clip['start'] = clip.pop('start_point', 0)
                clip['end'] = clip.pop('end_point', 0)
                return clip
            return None
        except Exception as e:
            logging.error(f"Error adding clip: {str(e)}")
            return None
    
    # System Settings
    def set_system_setting(self, key, value):
        """Set or update a system setting"""
        try:
            now = datetime.now()
            
            # Try to update first
            self._execute_query(
                "UPDATE system_settings SET value = %s, updated_at = %s WHERE key = %s",
                (value, now, key),
                fetch=False
            )
            
            # Get number of affected rows
            conn, cursor = self._get_connection()
            
            # If no rows affected, insert new setting
            if cursor.rowcount == 0:
                self._execute_query(
                    "INSERT INTO system_settings (key, value, updated_at) VALUES (%s, %s, %s)",
                    (key, value, now),
                    fetch=False
                )
            
            return True
        except Exception as e:
            logging.error(f"Error setting system setting: {str(e)}")
            return False
    
    def get_system_setting(self, key, default=None):
        """Get a system setting value"""
        try:
            result = self._execute_query(
                "SELECT value FROM system_settings WHERE key = %s",
                (key,)
            )
            
            if result and len(result) > 0:
                return result[0]['value']
            return default
        except Exception as e:
            logging.error(f"Error getting system setting: {str(e)}")
            return default

# Demo database for testing/development
class DemoDatabase:
    """Simple in-memory database for demo/testing"""
    def __init__(self):
        self.users = {
            "admin": {
                "id": "admin-uuid",
                "username": "admin",
                "password_hash": "admin-hash",
                "email": "admin@example.com",
                "role": "admin",
                "created_at": datetime.now()
            }
        }
        self.projects = {}
        self.assets = {}
        self.exports = {}
        self.settings = {}
        self.credits = {"admin-uuid": {"total": 1000, "used": 0, "transactions": []}}
        self.logs = []
        
    def get_user_by_username(self, username):
        return self.users.get(username)
        
    def list_all_users(self):
        return list(self.users.values())
        
    def get_user_credits(self, user_id):
        return self.credits.get(user_id)
        
    def get_system_setting(self, name, default=None):
        return self.settings.get(name, default)
        
    def set_system_setting(self, name, value):
        self.settings[name] = value
        return True
        
    def cleanup_expired_sessions(self):
        pass
        
    def create_user(self, **kwargs):
        user_id = kwargs.get('user_id')
        self.users[kwargs.get('username')] = kwargs
        return user_id
        
    def add_credits(self, **kwargs):
        user_id = kwargs.get('user_id')
        if user_id not in self.credits:
            self.credits[user_id] = {"total": 0, "used": 0, "transactions": []}
        self.credits[user_id]["total"] += kwargs.get('amount', 0)
        tx = {
            "amount": kwargs.get('amount', 0),
            "description": kwargs.get('description', ''),
            "timestamp": datetime.now()
        }
        self.credits[user_id]["transactions"].append(tx)
        return True
        
    def get_project_assets(self, project_id):
        return self.assets.get(project_id, [])
        
    def add_log(self, level, message, source=None, user_id=None, ip_address=None, request_path=None):
        """Add a log entry"""
        log_entry = {
            "timestamp": datetime.now(),
            "level": level,
            "message": message,
            "source": source,
            "user_id": user_id,
            "ip_address": ip_address,
            "request_path": request_path
        }
        self.logs.append(log_entry)
        print(f"LOG: [{level}] {message}")
        return True

class Database:
    def __init__(self, db_path=None, use_postgres=True, 
                 host='localhost', port=5432, database='flux58',
                 user='postgres', password='postgres'):
        """Initialize database with PostgreSQL backend"""
        self.use_postgres = True  # Always use PostgreSQL
        
        try:
            # Check if psycopg2 is available
            try:
                import psycopg2
                POSTGRES_AVAILABLE = True
                logging.info("PostgreSQL support is available")
            except ImportError:
                POSTGRES_AVAILABLE = False
                logging.error("PostgreSQL support not available - psycopg2 not installed")
                
            # Use PostgreSQL as the database backend if available
            if POSTGRES_AVAILABLE:
                self.pg_db = PostgresDatabase(
                    host=host,
                    port=port,
                    database=database,
                    user=user,
                    password=password
                )
                print("Using PostgreSQL database")
            else:
                raise ImportError("PostgreSQL support not available")
        except Exception as e:
            # Fall back to demo database
            print(f"Warning: PostgreSQL database not available, using placeholder implementation: {str(e)}")
            self.pg_db = DemoDatabase()
            self.use_postgres = False
            print("Using demo database for testing")
    
    # Connection management - act as pass-through to PostgreSQL
    def _connect(self):
        """Connect to database - no-op for PostgreSQL"""
        pass
    
    def _disconnect(self):
        """Disconnect from database - no-op for PostgreSQL"""
        pass
    
    def _initialize_db(self):
        """Initialize database tables - handled by PostgresDatabase"""
        pass
    
    # All methods below are pass-through to PostgreSQL implementation
    
    # User Management Methods
    def create_user(self, user_id, username, password_hash, email, role="user"):
        """Create a new user"""
        return self.pg_db.create_user(user_id, username, password_hash, email, role)
    
    def get_user_by_username(self, username):
        """Get user by username"""
        return self.pg_db.get_user_by_username(username)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        return self.pg_db.get_user_by_id(user_id)
    
    def update_user(self, user_id, email=None, password_hash=None, role=None):
        """Update user details"""
        return self.pg_db.update_user(user_id, email, password_hash, role)
    
    def delete_user(self, user_id):
        """Delete user"""
        return self.pg_db.delete_user(user_id)
    
    def list_all_users(self):
        """List all users"""
        return self.pg_db.list_all_users()
    
    # Session Management Methods
    def create_session(self, token, user_id, username, expires_at):
        """Create a new session"""
        return self.pg_db.create_session(token, user_id, username, expires_at)
    
    def get_session(self, token):
        """Get session by token"""
        return self.pg_db.get_session(token)
    
    def delete_session(self, token):
        """Delete session"""
        return self.pg_db.delete_session(token)
    
    def cleanup_expired_sessions(self):
        """Delete expired sessions"""
        return self.pg_db.cleanup_expired_sessions()
    
    # Credit Management Methods
    def get_user_credits(self, user_id):
        """Get user's credit information"""
        return self.pg_db.get_user_credits(user_id)
    
    def add_credits(self, user_id, amount, transaction_type, description="", status="completed"):
        """Add credits to user account"""
        return self.pg_db.add_credits(user_id, amount, transaction_type, description, status)
    
    def use_credits(self, user_id, amount, description="", transaction_type="usage", status="completed"):
        """Use credits from user account"""
        return self.pg_db.use_credits(user_id, amount, description, transaction_type, status)
    
    # Project Management Methods
    def create_project(self, project_id, user_id, name, description=""):
        """Create a new project"""
        return self.pg_db.create_project(project_id, user_id, name, description)
    
    def get_project(self, project_id):
        """Get project by ID including all related data"""
        return self.pg_db.get_project(project_id)
    
    def update_project(self, project_id, name=None, description=None):
        """Update project metadata"""
        return self.pg_db.update_project(project_id, name, description)
    
    def delete_project(self, project_id):
        """Delete project and all related data"""
        return self.pg_db.delete_project(project_id)
    
    def list_user_projects(self, user_id):
        """List projects for a user"""
        return self.pg_db.list_user_projects(user_id)
    
    # Asset Management Methods
    def add_asset(self, asset):
        """Add an asset to a project"""
        if not isinstance(asset, dict):
            return None
        
        asset_id = asset.get('id')
        project_id = asset.get('project_id')
        name = asset.get('name')
        path = asset.get('path')
        asset_type = asset.get('type')
        
        if not all([asset_id, project_id, name, path, asset_type]):
            return None
        
        # Extract filename from path
        filename = os.path.basename(path)
        
        return self.pg_db.add_asset(asset_id, project_id, name, filename, path, asset_type)
    
    def get_asset(self, asset_id):
        """Get asset by ID"""
        return self.pg_db.get_asset(asset_id)
        
    def get_project_assets(self, project_id):
        """Get all assets for a project"""
        try:
            # Get the assets from the project
            project = self.get_project(project_id)
            if project and 'assets' in project:
                return project['assets']
            return []
        except Exception as e:
            logging.error(f"Error getting project assets: {str(e)}")
            return []
            
    def delete_asset(self, asset_id):
        """Delete an asset"""
        try:
            # Pass through to PostgreSQL implementation
            conn, cursor = self.pg_db._get_connection()
            cursor.execute(
                "DELETE FROM project_assets WHERE id = %s",
                (asset_id,)
            )
            conn.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error deleting asset: {str(e)}")
            return False
    
    # Timeline Management Methods
    def add_track(self, track_id, project_id, name):
        """Add a track to a project timeline"""
        return self.pg_db.add_track(track_id, project_id, name)
    
    def add_clip(self, clip_id, track_id, asset_id, position, duration, start=0, end=None, properties=None):
        """Add a clip to a timeline track"""
        return self.pg_db.add_clip(clip_id, track_id, asset_id, position, duration, start, end, properties)
    
    # System Settings
    def set_system_setting(self, key, value):
        """Set or update a system setting"""
        return self.pg_db.set_system_setting(key, value)
    
    def get_system_setting(self, key, default=None):
        """Get a system setting value"""
        return self.pg_db.get_system_setting(key, default)
    
    # Logging System
    def add_log(self, level, module, message, user_id=None, ip_address=None):
        """Add a log entry to the system log"""
        return self.pg_db.add_log(level, module, message, user_id, ip_address)

#----------------------------------------------------------
# Project Management System
#----------------------------------------------------------

class ProjectManager:
    def __init__(self, database, base_path=None):
        """Initialize the project manager with a database connection"""
        if base_path is None:
            base_path = DATA_DIR
            
        self.db = database
        self.projects_path = os.path.join(base_path, 'projects')
        self.exports_path = os.path.join(base_path, 'exports')
        
        # Ensure directories exist
        os.makedirs(self.projects_path, exist_ok=True)
        os.makedirs(self.exports_path, exist_ok=True)
    
    def create_project(self, user_id, project_name, description=""):
        """Create a new OpenShot project"""
        project_id = str(uuid.uuid4())
        
        # Create project directory
        project_dir = os.path.join(self.projects_path, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # Create project in database
        project = self.db.create_project(project_id, user_id, project_name, description)
        
        if not project:
            # Clean up directory if database creation failed
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            return None
        
        # Create project file for OpenShot integration
        self._save_project_file(project_id, project)
        
        return project
    
    def get_project(self, project_id):
        """Get a project by ID"""
        # Get project from database
        project = self.db.get_project(project_id)
        
        if not project:
            return None
        
        # Ensure project file exists
        if project:
            try:
                self._save_project_file(project_id, project)
            except Exception as e:
                print(f"Warning: Could not save project file: {str(e)}")
        
        return project
    
    def update_project(self, project_id, name=None, description=None):
        """Update project data"""
        # Update in database
        success = self.db.update_project(project_id, name, description)
        
        if not success:
            return None
        
        # Get updated project
        project = self.db.get_project(project_id)
        
        if project:
            # Update project file
            self._save_project_file(project_id, project)
        
        return project
    
    def delete_project(self, project_id):
        """Delete a project"""
        # Delete from database
        success = self.db.delete_project(project_id)
        
        if not success:
            return False
        
        # Delete project directory
        project_dir = os.path.join(self.projects_path, project_id)
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        
        return True
    
    def list_user_projects(self, user_id):
        """List all projects for a user"""
        return self.db.list_user_projects(user_id)
    
    def add_asset(self, project_id, file_path, asset_type, name=None):
        """Add an asset to a project"""
        project = self.get_project(project_id)
        
        if not project:
            return None
        
        # Generate asset ID and filename
        asset_id = str(uuid.uuid4())
        filename = os.path.basename(file_path)
        
        if not name:
            name = filename
        
        # Copy file to project assets directory
        assets_dir = os.path.join(self.projects_path, project_id, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        target_path = os.path.join(assets_dir, f"{asset_id}_{filename}")
        shutil.copy2(file_path, target_path)
        
        # Add asset to database
        asset = {
            'id': asset_id,
            'project_id': project_id,
            'name': name,
            'path': target_path,
            'type': asset_type
        }
        asset = self.db.add_asset(asset)
        
        # Update project file
        if asset:
            project = self.get_project(project_id)
            self._save_project_file(project_id, project)
        
        return asset
    
    def add_clip_to_timeline(self, project_id, asset_id, track_id, position, duration):
        """Add a clip to the timeline"""
        project = self.get_project(project_id)
        
        if not project:
            return None
        
        # Find the asset
        asset = None
        for a in project["assets"]:
            if a["id"] == asset_id:
                asset = a
                break
        
        if not asset:
            return None
        
        # Find or create track
        track = None
        track_exists = False
        
        # Look for track in project
        for t in project["timeline"]["tracks"]:
            if t["id"] == track_id:
                track = t
                track_exists = True
                break
        
        # If track doesn't exist, create it
        if not track:
            track_name = f"Track {len(project['timeline']['tracks']) + 1}"
            track = self.db.add_track(track_id, project_id, track_name)
            
            if not track:
                return None
        
        # Create clip
        clip_id = str(uuid.uuid4())
        clip = self.db.add_clip(
            clip_id=clip_id,
            track_id=track_id,
            asset_id=asset_id,
            position=position,
            duration=duration
        )
        
        if clip:
            # Update project file
            project = self.get_project(project_id)
            self._save_project_file(project_id, project)
        
        return clip
    
    def _save_project_file(self, project_id, project_data):
        """Save project data to file"""
        try:
            project_dir = os.path.join(self.projects_path, project_id)
            os.makedirs(project_dir, exist_ok=True)
            
            project_file = os.path.join(project_dir, "project.json")
            
            # Create a clean copy of project data for OpenShot
            openshot_project = {
                "id": project_data.get("id", project_id),
                "name": project_data.get("name", "Untitled Project"),
                "description": project_data.get("description", ""),
                "user_id": project_data.get("user_id", ""),
                "created_at": project_data.get("created_at", datetime.now().isoformat()),
                "updated_at": project_data.get("updated_at", datetime.now().isoformat()),
                "assets": [],
                "timeline": project_data.get("timeline", {
                    "duration": 60,
                    "width": 1920,
                    "height": 1080,
                    "fps": {
                        "num": 30,
                        "den": 1
                    },
                    "sample_rate": 48000,
                    "channels": 2,
                    "channel_layout": 3,
                    "tracks": []
                })
            }
            
            # Ensure timeline has proper structure
            if not isinstance(openshot_project["timeline"], dict):
                openshot_project["timeline"] = {
                    "duration": 60,
                    "width": 1920,
                    "height": 1080,
                    "fps": {"num": 30, "den": 1},
                    "sample_rate": 48000,
                    "channels": 2,
                    "channel_layout": 3,
                    "tracks": []
                }
            
            # Ensure timeline tracks exists and is a list
            if "tracks" not in openshot_project["timeline"] or not isinstance(openshot_project["timeline"]["tracks"], list):
                openshot_project["timeline"]["tracks"] = []
            
            # Process assets to make sure file paths are correct
            if project_data.get("assets") and isinstance(project_data.get("assets"), list):
                for asset in project_data.get("assets", []):
                    if not isinstance(asset, dict):
                        continue
                        
                    asset_copy = dict(asset)
                    
                    # Ensure asset path is accessible to OpenShot
                    if "path" in asset_copy and not os.path.exists(asset_copy["path"]):
                        # Try to fix path if it's a relative path
                        if "id" in asset_copy and "filename" in asset_copy:
                            potential_path = os.path.join(project_dir, "assets", 
                                                        f"{asset_copy['id']}_{asset_copy['filename']}")
                            if os.path.exists(potential_path):
                                asset_copy["path"] = potential_path
                    
                    openshot_project["assets"].append(asset_copy)
            
            # Make sure all clips have reference to asset paths for export
            for track in openshot_project["timeline"].get("tracks", []):
                if isinstance(track, dict) and "clips" in track and isinstance(track["clips"], list):
                    for clip in track.get("clips", []):
                        if not isinstance(clip, dict):
                            continue
                            
                        # Find associated asset for this clip
                        asset_id = clip.get("asset_id")
                        if asset_id:
                            for asset in openshot_project["assets"]:
                                if asset.get("id") == asset_id:
                                    clip["asset_path"] = asset.get("path", "")
                                    break
            
            # Convert datetime objects to strings for JSON serialization
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Type {type(obj)} not serializable")
                
            # Save to file
            with open(project_file, 'w') as f:
                json.dump(openshot_project, f, indent=2, default=json_serializer)
        except Exception as e:
            logging.error(f"Error saving project file: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())

#----------------------------------------------------------
# Main Function
#----------------------------------------------------------

def create_admin_user(db, username="admin", password="admin123", email="admin@example.com"):
    """Create an admin user if it doesn't exist"""
    # Check if admin user exists
    admin = db.get_user_by_username(username)
    
    if not admin:
        # Create admin user
        user_id = str(uuid.uuid4())
        password_hash = generate_password_hash(password)
        
        success = db.create_user(
            user_id=user_id,
            username=username,
            password_hash=password_hash,
            email=email,
            role="admin"
        )
        
        if success:
            # Add initial credits
            db.add_credits(
                user_id=user_id,
                amount=1000,
                transaction_type="initial",
                description="Initial admin credits",
                status="completed"
            )
            
            print(f"Created admin user: {username}")
            return True
    else:
        print(f"Admin user {username} already exists")
    
    return False

if __name__ == "__main__":
    # Initialize logger
    init_logger(log_dir=LOGS_DIR, log_level=logging.INFO)
    
    # Initialize database
    db = Database(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    
    # Create admin user if needed
    create_admin_user(db)
    
    # Initialize project manager
    project_manager = ProjectManager(db)
    
    print("FLUX58 AI MEDIA LABS Consolidated Application Initialized")
    print(f"Base directory: {BASE_DIR}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Using PostgreSQL: {db.use_postgres}")
    print("\nTo run the web application, use:")
    print("    cd " + BASE_DIR)
    print("    python app.py")