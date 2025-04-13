from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('openshot_service.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///openshot_service.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

try:
    import openshot
    OPENSHOT_AVAILABLE = True
    logger.info("OpenShot library successfully imported")
except ImportError:
    OPENSHOT_AVAILABLE = False
    logger.warning("OpenShot library not available")

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_type = db.Column(db.String(50), nullable=False)
    parameters = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    result = db.Column(db.Text, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            "service": "OpenShot Processing Service",
            "status": "running",
            "openshot_available": OPENSHOT_AVAILABLE
        })
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    logger.info(f"Login attempt for user: {data.get('username')}")
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.password == data.get('password'):
        login_user(user)
        logger.info(f"User {user.username} logged in successfully")
        return jsonify({"message": "Login successful", "user_id": user.id})
    logger.warning(f"Failed login attempt for user: {data.get('username')}")
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"})

@app.route('/submit-job', methods=['POST'])
@login_required
def submit_job():
    data = request.json
    job_type = data.get('job_type')
    parameters = data.get('parameters')
    
    if not job_type:
        return jsonify({"error": "Job type is required"}), 400
        
    new_job = Job(
        user_id=current_user.id,
        job_type=job_type,
        parameters=parameters
    )
    
    db.session.add(new_job)
    db.session.commit()
    
    logger.info(f"Job submitted: {job_type} by user {current_user.id}")
    return jsonify({
        "message": "Job submitted successfully", 
        "job_id": new_job.id,
        "status": new_job.status
    })

@app.route('/job/<int:job_id>', methods=['GET'])
@login_required
def get_job_status(job_id):
    job = Job.query.get(job_id)
    
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    if job.user_id != current_user.id:
        return jsonify({"error": "Unauthorized access"}), 403
        
    return jsonify({
        "job_id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "result": job.result
    })

@app.route('/user/jobs', methods=['GET'])
@login_required
def get_user_jobs():
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    job_list = [{
        "job_id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    } for job in jobs]
    
    return jsonify({"jobs": job_list})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    if not username or not password or not email:
        return jsonify({"error": "Username, password and email are required"}), 400
        
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400
        
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        return jsonify({"error": "Email already registered"}), 400
        
    new_user = User(username=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()
    
    logger.info(f"New user registered: {username}")
    return jsonify({"message": "User registered successfully"})

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "openshot_available": OPENSHOT_AVAILABLE,
        "database": "connected" if db.engine.pool.checkedout() >= 0 else "error"
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {str(e)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)