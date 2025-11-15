# Media Gallery Web Application

A secure, password-protected web application for uploading, viewing, and managing photos and videos. Built with Flask and Python, supporting both local storage and AWS S3.

## Features

- **Password Authentication**: Secure login system to protect your media
- **Multi-file Upload**: Upload multiple photos and videos simultaneously
- **Dual Storage Options**: Store files locally or on AWS S3
- **Gallery View**: Beautiful grid layout to browse your media
- **Media Viewer**: Click to view full-size images and play videos
- **Admin Panel**: Manage all uploaded media with easy download options
- **Bulk Download**: Download selected files or all files as a ZIP archive
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
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your-secure-password
   ```

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

   Use the credentials you set in the `.env` file:
   - Username: `admin` (or your custom username)
   - Password: `admin123` (or your custom password)

## Usage Guide

### Uploading Media

1. Click **Upload** in the navigation menu
2. Click the upload area or drag and drop files
3. Select one or more photos/videos
4. Click **Upload Files**
5. Wait for the upload to complete

### Viewing Media

1. Click **Gallery** to see all uploaded media
2. Click on any image or video to view it full-size
3. Use the close button (×) or press ESC to close the viewer

### Admin Features

1. Click **Admin** to access the admin panel
2. **Download Individual Files**: Click the Download button for any file
3. **Download Selected Files**:
   - Check the boxes next to files you want
   - Click "Download Selected"
4. **Download All Files**: Click "Download All" to get everything as a ZIP

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

1. **Change Default Password**: Always change the default admin password in production
2. **Use Strong Secret Key**: Generate a strong, random SECRET_KEY
3. **HTTPS in Production**: Always use HTTPS in production environments
4. **Secure AWS Credentials**: Never commit AWS credentials to version control
5. **File Size Limits**: Default max file size is 500MB (configurable in `config.py`)

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
- Verify credentials in `.env` file
- Check that `.env` file exists and is being read
- Clear browser cookies and try again

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please create an issue in the repository.
