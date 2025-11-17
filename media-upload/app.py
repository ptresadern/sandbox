import os
import io
import zipfile
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import ClientError
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload folder if it doesn't exist
if app.config['STORAGE_TYPE'] == 'local':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class User(UserMixin):
    """Simple user class for authentication"""
    def __init__(self, id, role='user'):
        self.id = id
        self.role = role

    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'


@login_manager.user_loader
def load_user(user_id):
    """Load user from session"""
    users = app.config['USERS']
    if user_id in users:
        return User(user_id, users[user_id]['role'])
    return None


def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_s3_client():
    """Initialize and return S3 client"""
    return boto3.client(
        's3',
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=app.config['AWS_REGION']
    )


def upload_to_s3(file, filename):
    """Upload file to S3 bucket"""
    try:
        s3_client = get_s3_client()
        s3_path = f"{app.config['UPLOAD_FOLDER']}/{filename}"
        s3_client.upload_fileobj(
            file,
            app.config['S3_BUCKET_NAME'],
            s3_path,
            ExtraArgs={'ContentType': file.content_type}
        )
        return True
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return False


def upload_to_local(file, filename):
    """Upload file to local storage"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return True
    except Exception as e:
        print(f"Error uploading to local storage: {e}")
        return False


def get_media_files():
    """Get list of all media files from storage"""
    files = []

    if app.config['STORAGE_TYPE'] == 's3':
        try:
            s3_client = get_s3_client()
            prefix = f"{app.config['UPLOAD_FOLDER']}/"
            response = s3_client.list_objects_v2(
                Bucket=app.config['S3_BUCKET_NAME'],
                Prefix=prefix
            )

            if 'Contents' in response:
                for obj in response['Contents']:
                    filename = obj['Key'].replace(prefix, '')
                    if filename and allowed_file(filename):
                        files.append({
                            'name': filename,
                            'size': obj['Size'],
                            'modified': obj['LastModified'],
                            'url': get_file_url(filename)
                        })
        except ClientError as e:
            print(f"Error listing S3 files: {e}")
    else:
        # Local storage
        upload_folder = Path(app.config['UPLOAD_FOLDER'])
        if upload_folder.exists():
            for filepath in upload_folder.iterdir():
                if filepath.is_file() and allowed_file(filepath.name):
                    stat = filepath.stat()
                    files.append({
                        'name': filepath.name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'url': url_for('serve_file', filename=filepath.name)
                    })

    # Sort by modified date, newest first
    files.sort(key=lambda x: x['modified'], reverse=True)
    return files


def get_file_url(filename):
    """Get URL for a file"""
    if app.config['STORAGE_TYPE'] == 's3':
        s3_client = get_s3_client()
        s3_path = f"{app.config['UPLOAD_FOLDER']}/{filename}"
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': app.config['S3_BUCKET_NAME'], 'Key': s3_path},
                ExpiresIn=3600  # URL expires in 1 hour
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    else:
        return url_for('serve_file', filename=filename)


def get_file_type(filename):
    """Determine if file is image or video"""
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}:
        return 'image'
    elif ext in {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm'}:
        return 'video'
    return 'unknown'


@app.route('/')
def index():
    """Redirect to gallery if logged in, otherwise to login"""
    if current_user.is_authenticated:
        return redirect(url_for('gallery'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = app.config['USERS']
        if username in users and password == users[username]['password']:
            user = User(username, users[username]['role'])
            login_user(user)
            flash(f'Successfully logged in as {users[username]["role"]}!', 'success')
            return redirect(url_for('gallery'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('Successfully logged out', 'success')
    return redirect(url_for('login'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload page"""
    if request.method == 'POST':
        if 'files' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)

        files = request.files.getlist('files')
        uploaded_count = 0

        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to prevent duplicates
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename

                if app.config['STORAGE_TYPE'] == 's3':
                    if upload_to_s3(file, filename):
                        uploaded_count += 1
                    else:
                        flash(f'Failed to upload {file.filename} to S3', 'error')
                else:
                    if upload_to_local(file, filename):
                        uploaded_count += 1
                    else:
                        flash(f'Failed to upload {file.filename}', 'error')
            elif file and file.filename:
                flash(f'File type not allowed: {file.filename}', 'error')

        if uploaded_count > 0:
            flash(f'Successfully uploaded {uploaded_count} file(s)', 'success')

        return redirect(url_for('gallery'))

    return render_template('upload.html', storage_type=app.config['STORAGE_TYPE'])


@app.route('/gallery')
@login_required
def gallery():
    """Gallery page to view all uploaded media"""
    files = get_media_files()

    # Add file type to each file
    for file in files:
        file['type'] = get_file_type(file['name'])

    return render_template('gallery.html', files=files)


@app.route('/admin')
@login_required
def admin():
    """Admin page for managing and downloading media"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('gallery'))

    files = get_media_files()

    # Add file type to each file
    for file in files:
        file['type'] = get_file_type(file['name'])

    return render_template('admin.html', files=files, storage_type=app.config['STORAGE_TYPE'])


@app.route('/download/<filename>')
@login_required
def download_file(filename):
    """Download a single file - Admin only"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('gallery'))

    if not allowed_file(filename):
        flash('Invalid file', 'error')
        return redirect(url_for('admin'))

    if app.config['STORAGE_TYPE'] == 's3':
        try:
            s3_client = get_s3_client()
            s3_path = f"{app.config['UPLOAD_FOLDER']}/{filename}"

            # Get file from S3
            file_obj = io.BytesIO()
            s3_client.download_fileobj(app.config['S3_BUCKET_NAME'], s3_path, file_obj)
            file_obj.seek(0)

            return send_file(
                file_obj,
                as_attachment=True,
                download_name=filename
            )
        except ClientError as e:
            flash(f'Error downloading file: {e}', 'error')
            return redirect(url_for('admin'))
    else:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            flash('File not found', 'error')
            return redirect(url_for('admin'))


@app.route('/download-all')
@login_required
def download_all():
    """Download all files as a zip archive - Admin only"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('gallery'))

    files = get_media_files()

    if not files:
        flash('No files to download', 'error')
        return redirect(url_for('admin'))

    # Create a zip file in memory
    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        if app.config['STORAGE_TYPE'] == 's3':
            s3_client = get_s3_client()
            for file in files:
                try:
                    s3_path = f"{app.config['UPLOAD_FOLDER']}/{file['name']}"
                    file_obj = io.BytesIO()
                    s3_client.download_fileobj(app.config['S3_BUCKET_NAME'], s3_path, file_obj)
                    zf.writestr(file['name'], file_obj.getvalue())
                except ClientError as e:
                    print(f"Error downloading {file['name']}: {e}")
        else:
            for file in files:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file['name'])
                if os.path.exists(filepath):
                    zf.write(filepath, file['name'])

    memory_file.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'media_gallery_{timestamp}.zip'
    )


@app.route('/download-selected', methods=['POST'])
@login_required
def download_selected():
    """Download selected files as a zip archive - Admin only"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('gallery'))

    selected_files = request.form.getlist('selected_files')

    if not selected_files:
        flash('No files selected', 'error')
        return redirect(url_for('admin'))

    # Create a zip file in memory
    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        if app.config['STORAGE_TYPE'] == 's3':
            s3_client = get_s3_client()
            for filename in selected_files:
                if allowed_file(filename):
                    try:
                        s3_path = f"{app.config['UPLOAD_FOLDER']}/{filename}"
                        file_obj = io.BytesIO()
                        s3_client.download_fileobj(app.config['S3_BUCKET_NAME'], s3_path, file_obj)
                        zf.writestr(filename, file_obj.getvalue())
                    except ClientError as e:
                        print(f"Error downloading {filename}: {e}")
        else:
            for filename in selected_files:
                if allowed_file(filename):
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    if os.path.exists(filepath):
                        zf.write(filepath, filename)

    memory_file.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'media_selected_{timestamp}.zip'
    )


@app.route('/serve/<filename>')
@login_required
def serve_file(filename):
    """Serve a file for viewing (local storage only)"""
    if app.config['STORAGE_TYPE'] == 'local' and allowed_file(filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath)

    return "File not found", 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
