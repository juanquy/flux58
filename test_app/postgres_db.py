import os
import json
import uuid
from datetime import datetime, timedelta
import threading
import logging

# Thread-local storage for database connections
_thread_local = threading.local()

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
            if not hasattr(_thread_local, 'pg_connection'):
                # Create a new connection for this thread
                _thread_local.pg_connection = psycopg2.connect(**self.db_params)
                # Enable automatic commit on close
                _thread_local.pg_connection.autocommit = False
                # Use RealDictCursor to return query results as dictionaries
                _thread_local.pg_cursor = _thread_local.pg_connection.cursor(
                    cursor_factory=psycopg2.extras.RealDictCursor
                )
            
            return _thread_local.pg_connection, _thread_local.pg_cursor
        except ImportError:
            logging.error("psycopg2 module not found. Please install with 'pip install psycopg2-binary'")
            raise
        except Exception as e:
            logging.error(f"Error connecting to PostgreSQL: {str(e)}")
            raise
    
    def _close_connection(self, commit=True):
        """Close the thread-local database connection"""
        if hasattr(_thread_local, 'pg_connection'):
            if commit:
                _thread_local.pg_connection.commit()
            _thread_local.pg_cursor.close()
            _thread_local.pg_connection.close()
            del _thread_local.pg_cursor
            del _thread_local.pg_connection
    
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
    
    # Export Management Methods
    def create_export_job(self, export_id, project_id, user_id, output_path, 
                          format="mp4", width=1920, height=1080, fps=30,
                          video_bitrate="8000k", audio_bitrate="192k",
                          start_frame=1, end_frame=None):
        """Create a new export job"""
        try:
            now = datetime.now()
            
            self._execute_query(
                """INSERT INTO export_jobs
                   (id, project_id, user_id, output_path, format, width, height,
                    fps, video_bitrate, audio_bitrate, start_frame, end_frame,
                    started_at, status, priority, progress)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (export_id, project_id, user_id, output_path, format, width, height,
                 fps, video_bitrate, audio_bitrate, start_frame, end_frame,
                 now, "pending", 0, 0.0),
                fetch=False
            )
            
            result = self._execute_query(
                "SELECT * FROM export_jobs WHERE id = %s",
                (export_id,)
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
        except Exception as e:
            logging.error(f"Error creating export job: {str(e)}")
            return None
    
    def create_export_job_with_priority(self, export_id, project_id, user_id, output_path, 
                                       format="mp4", width=1920, height=1080, fps=30,
                                       video_bitrate="8000k", audio_bitrate="192k",
                                       start_frame=1, end_frame=None, priority=0):
        """Create a new export job with priority"""
        try:
            now = datetime.now()
            
            self._execute_query(
                """INSERT INTO export_jobs
                   (id, project_id, user_id, output_path, format, width, height,
                    fps, video_bitrate, audio_bitrate, start_frame, end_frame,
                    started_at, status, priority, progress)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (export_id, project_id, user_id, output_path, format, width, height,
                 fps, video_bitrate, audio_bitrate, start_frame, end_frame,
                 now, "pending", priority, 0.0),
                fetch=False
            )
            
            result = self._execute_query(
                "SELECT * FROM export_jobs WHERE id = %s",
                (export_id,)
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
        except Exception as e:
            logging.error(f"Error creating export job with priority: {str(e)}")
            return None
    
    def update_export_status(self, export_id, status, completed_at=None):
        """Update export job status"""
        try:
            if completed_at:
                self._execute_query(
                    "UPDATE export_jobs SET status = %s, completed_at = %s WHERE id = %s",
                    (status, completed_at, export_id),
                    fetch=False
                )
            else:
                self._execute_query(
                    "UPDATE export_jobs SET status = %s WHERE id = %s",
                    (status, export_id),
                    fetch=False
                )
            
            # Get number of affected rows
            conn, cursor = self._get_connection()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error updating export status: {str(e)}")
            return False
    
    def update_export_progress(self, export_id, progress, status=None):
        """Update export job progress"""
        try:
            if status:
                self._execute_query(
                    "UPDATE export_jobs SET progress = %s, status = %s WHERE id = %s",
                    (progress, status, export_id),
                    fetch=False
                )
            else:
                self._execute_query(
                    "UPDATE export_jobs SET progress = %s WHERE id = %s",
                    (progress, export_id),
                    fetch=False
                )
            
            # Get number of affected rows
            conn, cursor = self._get_connection()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error updating export progress: {str(e)}")
            return False
    
    def get_export_job(self, export_id):
        """Get export job by ID"""
        try:
            result = self._execute_query(
                "SELECT * FROM export_jobs WHERE id = %s",
                (export_id,)
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
        except Exception as e:
            logging.error(f"Error getting export job: {str(e)}")
            return None
    
    def get_next_pending_export(self):
        """Get the next pending export job with highest priority"""
        try:
            result = self._execute_query(
                """SELECT * FROM export_jobs 
                   WHERE status = 'pending' 
                   ORDER BY priority DESC, started_at ASC 
                   LIMIT 1"""
            )
            
            if result and len(result) > 0:
                return dict(result[0])
            return None
        except Exception as e:
            logging.error(f"Error getting next pending export: {str(e)}")
            return None
    
    def cancel_export_job(self, export_id):
        """Cancel an export job"""
        try:
            self._execute_query(
                "UPDATE export_jobs SET status = 'cancelled' WHERE id = %s AND status IN ('pending', 'processing')",
                (export_id,),
                fetch=False
            )
            
            # Get number of affected rows
            conn, cursor = self._get_connection()
            return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error cancelling export job: {str(e)}")
            return False
    
    def get_active_exports(self):
        """Get all currently processing export jobs"""
        try:
            result = self._execute_query(
                "SELECT * FROM export_jobs WHERE status = 'processing'"
            )
            
            return [dict(row) for row in result]
        except Exception as e:
            logging.error(f"Error getting active exports: {str(e)}")
            return []
    
    def list_user_exports(self, user_id):
        """List export jobs for a user"""
        try:
            result = self._execute_query(
                "SELECT * FROM export_jobs WHERE user_id = %s ORDER BY started_at DESC",
                (user_id,)
            )
            
            return [dict(row) for row in result]
        except Exception as e:
            logging.error(f"Error listing user exports: {str(e)}")
            return []
    
    # Logging System
    def add_log(self, level, module, message, user_id=None, ip_address=None):
        """Add a log entry to the system log"""
        try:
            now = datetime.now()
            
            self._execute_query(
                """INSERT INTO system_logs 
                   (timestamp, level, module, message, user_id, ip_address) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (now, level, module, message, user_id, ip_address),
                fetch=False
            )
            
            # Get the inserted row ID
            conn, cursor = self._get_connection()
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"Error adding log: {str(e)}")
            return None
    
    def get_logs(self, limit=100, offset=0, level=None, module=None, user_id=None):
        """Get system logs with filtering options"""
        try:
            query = "SELECT * FROM system_logs WHERE 1=1"
            params = []
            
            # Add filters
            if level:
                query += " AND level = %s"
                params.append(level)
            
            if module:
                query += " AND module = %s"
                params.append(module)
            
            if user_id:
                query += " AND user_id = %s"
                params.append(user_id)
            
            # Add ordering and limits
            query += " ORDER BY timestamp DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            result = self._execute_query(query, params)
            
            return [dict(row) for row in result]
        except Exception as e:
            logging.error(f"Error getting logs: {str(e)}")
            return []
    
    def clear_old_logs(self, days=30):
        """Clear logs older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            self._execute_query(
                "DELETE FROM system_logs WHERE timestamp < %s",
                (cutoff_date,),
                fetch=False
            )
            
            # Get number of affected rows
            conn, cursor = self._get_connection()
            return cursor.rowcount
        except Exception as e:
            logging.error(f"Error clearing old logs: {str(e)}")
            return 0
    
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
    
    def get_all_system_settings(self):
        """Get all system settings"""
        try:
            result = self._execute_query("SELECT * FROM system_settings")
            
            # Convert to dictionary with key as index
            settings = {}
            for row in result:
                settings[row['key']] = {
                    'value': row['value'],
                    'updated_at': row['updated_at']
                }
            
            return settings
        except Exception as e:
            logging.error(f"Error getting all system settings: {str(e)}")
            return {}
    
    # Database Maintenance
    def backup_database(self):
        """Create a backup of the database using pg_dump"""
        try:
            import subprocess
            import os
            
            # Get current timestamp for backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"postgres_backup_{timestamp}.sql"
            
            # Prepare pg_dump command
            env = os.environ.copy()
            env['PGPASSWORD'] = self.password
            
            cmd = [
                'pg_dump',
                '-h', self.host,
                '-p', str(self.port),
                '-U', self.user,
                '-d', self.database,
                '-f', backup_file,
                '-Fc'  # Custom format (compressed)
            ]
            
            # Run pg_dump
            result = subprocess.run(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'file': backup_file,
                    'size': os.path.getsize(backup_file) if os.path.exists(backup_file) else 0
                }
            else:
                logging.error(f"pg_dump error: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr
                }
        except Exception as e:
            logging.error(f"Error backing up database: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_database(self, backup_file):
        """Restore database from a backup file"""
        try:
            import subprocess
            import os
            
            if not os.path.exists(backup_file):
                return {
                    'success': False,
                    'error': f"Backup file {backup_file} not found"
                }
            
            # Prepare pg_restore command
            env = os.environ.copy()
            env['PGPASSWORD'] = self.password
            
            cmd = [
                'pg_restore',
                '-h', self.host,
                '-p', str(self.port),
                '-U', self.user,
                '-d', self.database,
                '-c',  # Clean (drop) database objects before recreating
                backup_file
            ]
            
            # Run pg_restore
            result = subprocess.run(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'message': "Database restored successfully"
                }
            else:
                logging.error(f"pg_restore error: {result.stderr}")
                return {
                    'success': False,
                    'error': result.stderr
                }
        except Exception as e:
            logging.error(f"Error restoring database: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_database_size(self):
        """Get the current size of the database"""
        try:
            result = self._execute_query("""
                SELECT pg_size_pretty(pg_database_size(%s)) as size,
                       pg_database_size(%s) as bytes
            """, (self.database, self.database))
            
            if result and len(result) > 0:
                return {
                    'size': result[0]['size'],
                    'bytes': result[0]['bytes']
                }
            return None
        except Exception as e:
            logging.error(f"Error getting database size: {str(e)}")
            return None
    
    def get_table_sizes(self):
        """Get the sizes of all tables in the database"""
        try:
            result = self._execute_query("""
                SELECT
                    table_name,
                    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size,
                    pg_total_relation_size(quote_ident(table_name)) as bytes
                FROM
                    information_schema.tables
                WHERE
                    table_schema = 'public'
                ORDER BY
                    pg_total_relation_size(quote_ident(table_name)) DESC
            """)
            
            return [dict(row) for row in result]
        except Exception as e:
            logging.error(f"Error getting table sizes: {str(e)}")
            return []
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            stats = {
                "tables": {},
                "size": self.get_database_size(),
                "last_backup": self.get_system_setting('last_backup_time', 'Never')
            }
            
            # Get row count for each table
            for table in ['users', 'sessions', 'credits', 'credit_transactions',
                          'projects', 'project_assets', 'project_timeline',
                          'timeline_tracks', 'timeline_clips', 'export_jobs',
                          'system_settings', 'system_logs']:
                
                result = self._execute_query(f"SELECT COUNT(*) as count FROM {table}")
                
                if result and len(result) > 0:
                    stats["tables"][table] = {
                        "rows": result[0]['count']
                    }
            
            # Get table sizes
            table_sizes = self.get_table_sizes()
            for table in table_sizes:
                table_name = table['table_name']
                if table_name in stats["tables"]:
                    stats["tables"][table_name]["size"] = table['size']
                    stats["tables"][table_name]["bytes"] = table['bytes']
            
            return stats
        except Exception as e:
            logging.error(f"Error getting database stats: {str(e)}")
            return {"error": str(e)}
    
    def analyze_database(self):
        """Run ANALYZE on all tables to update statistics"""
        try:
            self._execute_query("ANALYZE", fetch=False)
            return True
        except Exception as e:
            logging.error(f"Error analyzing database: {str(e)}")
            return False
    
    def vacuum_database(self):
        """Run VACUUM on all tables to reclaim space"""
        try:
            # Get size before vacuum
            size_before = self.get_database_size()
            
            # Can't use the regular connection for VACUUM
            import psycopg2
            vacuum_params = self.db_params.copy()
            vacuum_params['options'] = '-c statement_timeout=0'  # No timeout for VACUUM
            
            conn = psycopg2.connect(**vacuum_params)
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Run VACUUM ANALYZE
            cursor.execute("VACUUM ANALYZE")
            
            # Clean up
            cursor.close()
            conn.close()
            
            # Get size after vacuum
            size_after = self.get_database_size()
            
            return {
                "success": True,
                "size_before": size_before['size'] if size_before else "Unknown",
                "size_after": size_after['size'] if size_after else "Unknown",
                "size_reduction": (size_before['bytes'] - size_after['bytes']) if size_before and size_after else 0
            }
        except Exception as e:
            logging.error(f"Error vacuuming database: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }