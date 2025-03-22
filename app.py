from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import uuid
import threading
from datetime import datetime
from utils.video_tools import process_video, generate_captions, extract_audio, transcribe_audio, add_captions_to_video
from utils.file_converter import convert_file

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CONVERTED_FOLDER'] = 'converted'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'doc', 'docx', 'jpg', 'png', 'mp3', 'mp4', 'pptx', 'cdr', 'ai', 'psd', 'svg', 'mov', 'avi'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/lib/your-app/site.db'  # Persistent database location
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Ensure upload and converted folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['CONVERTED_FOLDER'], exist_ok=True)
os.makedirs('/var/lib/your-app', exist_ok=True)  # Ensure persistent database directory exists

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    files = db.relationship('FileHistory', backref='user', lazy=True)

class FileHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    converted_filename = db.Column(db.String(100), nullable=False)
    operation = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Helper functions
def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('All fields are required!', 'error')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken!', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/file_conversion')
def file_conversion():
    return render_template('file_conv.html')

@app.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    history = FileHistory.query.filter_by(user_id=user_id).order_by(FileHistory.timestamp.desc()).all()
    return render_template('history.html', history=history)

@app.route('/delete_entry/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    entry = FileHistory.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return '', 204  # No content response

@app.route('/download_history')
def download_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    history = FileHistory.query.filter_by(user_id=user_id).order_by(FileHistory.timestamp.desc()).all()
    
    csv_content = "Date,Operation,Filename,Status\n"
    for entry in history:
        csv_content += f"{entry.timestamp.strftime('%Y-%m-%d %H:%M')},{entry.operation},{entry.filename},Completed\n"
    
    response = Response(csv_content, mimetype='text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename='history.csv')
    return response

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# File upload and conversion
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    
    output_format = request.form.get('format')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            converted_file = convert_file(filepath, output_format)
            user_id = session['user_id']
            new_history = FileHistory(
                user_id=user_id,
                filename=filename,
                converted_filename=os.path.basename(converted_file),
                operation=f'Convert to {output_format}'
            )
            db.session.add(new_history)
            db.session.commit()
            return redirect(url_for('result1', filename=os.path.basename(converted_file)))
        except Exception as e:
            logging.error(f"Error processing file: {e}")
            flash('Error processing file', 'error')
            return redirect(request.url)
    else:
        flash('File type not allowed', 'error')
        return redirect(request.url)

# Video captioning
progress = 0  # Global variable to track progress

@app.route('/video_captioning', methods=['GET', 'POST'])
def video_captioning():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            dest_language = request.form.get('language', 'en')
            text_style = request.form.get('text-style', 'arial')
            text_size = request.form.get('text-size', '24')
            text_position = request.form.get('text-position', 'bottom')
            text_color = request.form.get('text-color', '#ffffff')

            output_filename = f"captioned_{filename}"
            output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
            thread = threading.Thread(
                target=process_video,
                args=(filepath, output_path, dest_language, text_style, text_size, text_position, text_color)
            )
            thread.start()

            return jsonify({"message": "Video processing started", "filename": output_filename}), 200
        else:
            return jsonify({"error": "File type not allowed"}), 400

    return render_template('video_captioning.html')

@app.route('/progress')
def get_progress():
    """Endpoint to fetch progress."""
    global progress
    return jsonify({"progress": progress})

# Result pages
@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename)

@app.route('/result1/<filename>')
def result1(filename):
    return render_template('result1.html', filename=filename)

# File download
@app.route('/converted/<filename>')
def converted_file(filename):
    return send_from_directory(app.config['CONVERTED_FOLDER'], filename)

@app.route('/download/<filename>')
def download_file(filename):
    if not filename:
        flash('No file specified', 'error')
        return redirect(url_for('dashboard'))

    filepath = os.path.join(app.config['CONVERTED_FOLDER'], filename)
    if not os.path.exists(filepath):
        logging.error(f"File not found: {filepath}")
        flash('File not found', 'error')
        return redirect(url_for('dashboard'))

    try:
        return send_from_directory(app.config['CONVERTED_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        flash('Error downloading file', 'error')
        return redirect(url_for('dashboard'))

# Initialize database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)