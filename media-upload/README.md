# Phil & Rachel's Wedding Album

A secure, password-protected web application for uploading, viewing, and managing photos and videos. Built with Flask and Python, supporting both local storage and AWS S3.

## Features

- **Role-Based Authentication**: Two-tier access control with admin and user roles
  - **Admin**: Full access including file downloads and management
  - **User**: View-only access for browsing media
- **Multi-file Upload**: Upload multiple photos and videos simultaneously
- **Dual Storage Options**: Store files locally or on AWS S3
- **Gallery View**: Beautiful grid layout to browse your media with adjustable columns (2-6 columns)
- **Media Viewer**: Click to view full-size images and play videos
- **Admin Panel**: Manage all uploaded media with easy download options (admin only)
- **Bulk Download**: Download selected files or all files as a ZIP archive (admin only)
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Supported File Formats

### Images
- PNG, JPG, JPEG, GIF, BMP, WebP

### Videos
- MP4, AVI, MOV, WMV, FLV, MKV, WebM

## Requirements

- Python 3.8 or higher
- pip (Python package manager)
- AWS Account (only if using S3 storage)

## Installation

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the application**

   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and update the following settings:

   ### Basic Configuration
   ```env
   SECRET_KEY=your-secret-key-here-change-this
   ADMIN_PASSWORD=your-secure-admin-password
   USER_PASSWORD=your-secure-user-password
   ```

   **Default User Accounts:**
   - Admin user: username `admin` (configurable password)
   - Regular user: username `user` (configurable password)

   See the "User Management" section below for adding additional users.

   ### Storage Configuration

   **For Local Storage (Default):**
   ```env
   STORAGE_TYPE=local
   UPLOAD_FOLDER=photo-gallery
   ```

   **For AWS S3 Storage:**
   ```env
   STORAGE_TYPE=s3
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=your-bucket-name
   ```

## Running the Application

1. **Start the Flask development server**
   ```bash
   python app.py
   ```

2. **Access the application**

   Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. **Login**

   Use one of the following credentials:

   **Admin Account (Full Access):**
   - Username: `admin`
   - Password: Set in `.env` as `ADMIN_PASSWORD` (default: `admin123`)

   **User Account (View Only):**
   - Username: `user`
   - Password: Set in `.env` as `USER_PASSWORD` (default: `user123`)

## Usage Guide

### Uploading Media

1. Click **Upload** in the navigation menu
2. Click the upload area or drag and drop files
3. Select one or more photos/videos
4. Click **Upload Files**
5. Wait for the upload to complete

### Viewing Media

1. Click **Gallery** to see all uploaded media
2. Use the **Columns** dropdown to adjust the gallery layout (2-6 columns)
   - Your preference is saved automatically in your browser
3. Click on any image or video to view it full-size
4. Use the close button (×) or press ESC to close the viewer

### Admin Features (Admin Role Only)

The Admin panel is only accessible to users with the admin role.

1. Click **Admin** to access the admin panel
2. **Download Individual Files**: Click the Download button for any file
3. **Download Selected Files**:
   - Check the boxes next to files you want
   - Click "Download Selected"
4. **Download All Files**: Click "Download All" to get everything as a ZIP

**Note**: Regular users can view and upload media but cannot download files.

## User Management

### User Roles

The application supports two types of user roles:

1. **Admin Role**
   - Full access to all features
   - Can upload and view media
   - Can access the Admin panel
   - Can download individual files, selected files, or all files
   - Can see the Admin navigation link

2. **User Role** (Non-Admin)
   - Can upload media files
   - Can view media in the gallery
   - **Cannot** download files
   - **Cannot** access the Admin panel
   - Admin link is hidden from navigation

### Adding New Users

To add new users with non-admin rights, edit the `config.py` file:

1. Open `media-upload/config.py` in a text editor

2. Locate the `USERS` dictionary (around line 13)

3. Add a new user entry following this format:

```python
USERS = {
    'admin': {
        'password': os.getenv('ADMIN_PASSWORD', 'admin123'),
        'role': 'admin'
    },
    'user': {
        'password': os.getenv('USER_PASSWORD', 'user123'),
        'role': 'user'
    },
    # Add your new user here
    'newusername': {
        'password': 'secure-password-here',  # Or use os.getenv('NEW_USER_PASSWORD', 'default')
        'role': 'user'  # Use 'user' for non-admin, 'admin' for admin
    }
}
```

4. Save the file and restart the application

### Using Environment Variables for User Passwords

For better security, store passwords in environment variables:

1. Add to your `.env` file:
```env
ADMIN_PASSWORD=your-secure-admin-password
USER_PASSWORD=your-secure-user-password
NEW_USER_PASSWORD=another-secure-password
```

2. Update `config.py` to reference the environment variable:
```python
'newusername': {
    'password': os.getenv('NEW_USER_PASSWORD', 'default-password'),
    'role': 'user'
}
```

### Best Practices for User Management

- Always use strong, unique passwords for each user
- Use environment variables for passwords in production
- Regularly review and remove unused accounts
- Consider implementing password hashing for production use
- Document who has admin access

## AWS S3 Setup (Optional)

If you want to use AWS S3 for storage:

1. **Create an S3 Bucket**
   - Go to AWS Console → S3
   - Create a new bucket
   - Note the bucket name and region

2. **Create IAM User**
   - Go to AWS Console → IAM
   - Create a new user with programmatic access
   - Attach policy: `AmazonS3FullAccess` (or create a custom policy)
   - Save the Access Key ID and Secret Access Key

3. **Configure Bucket Permissions**

   Add this CORS configuration to your S3 bucket:
   ```json
   [
       {
           "AllowedHeaders": ["*"],
           "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
           "AllowedOrigins": ["*"],
           "ExposeHeaders": []
       }
   ]
   ```

4. **Update .env File**

   Set your AWS credentials and bucket information in the `.env` file.

## Security Considerations

### Important Security Notes

1. **Change Default Passwords**: Always change all default passwords in production
2. **Use Strong Secret Key**: Generate a strong, random SECRET_KEY
3. **HTTPS in Production**: Always use HTTPS in production environments
4. **Secure AWS Credentials**: Never commit AWS credentials to version control
5. **File Size Limits**: Default max file size is 500MB (configurable in `config.py`)
6. **Password Storage**: Consider implementing password hashing (bcrypt, werkzeug) for production
7. **Environment Variables**: Store all sensitive credentials in environment variables, not in code

### Generating a Secure Secret Key

```python
import secrets
print(secrets.token_hex(32))
```

## Production Deployment

For production deployment, consider:

1. **Use a production WSGI server** (Gunicorn, uWSGI)
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Use a reverse proxy** (Nginx, Apache)
3. **Enable HTTPS** with SSL certificates
4. **Set environment variables** securely (don't use .env in production)
5. **Regular backups** of your media files
6. **Monitor disk space** if using local storage

## File Structure

```
media-gallery/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Example environment file
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── photo-gallery/        # Uploaded files (local storage)
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── upload.html
│   ├── gallery.html
│   └── admin.html
└── static/               # Static files
    └── css/
        └── style.css
```

## Troubleshooting

### Upload fails
- Check file size (max 500MB by default)
- Verify file format is supported
- Check disk space (local storage)
- Verify AWS credentials and permissions (S3 storage)

### Can't access S3 files
- Check AWS credentials in `.env`
- Verify S3 bucket permissions
- Check CORS configuration
- Ensure bucket region matches `.env` setting

### Login not working
- Verify credentials in `.env` file or `config.py`
- Check that `.env` file exists and is being read
- Ensure the username exists in the USERS dictionary in `config.py`
- Clear browser cookies and try again
- Check Flask console for error messages

### Can't access Admin panel
- Verify you're logged in with an admin role account
- Check that the user's role is set to 'admin' in `config.py`
- Non-admin users cannot access the Admin panel by design

### Column selector not working
- Ensure JavaScript is enabled in your browser
- Check browser console for errors
- Try clearing browser localStorage and refreshing

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
