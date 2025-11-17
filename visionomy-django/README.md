# Portfolio Website - Django

A modern portfolio website built with Django to showcase software development projects. Features include project descriptions, image galleries, videos, publications, and tag-based filtering.

## Features

- **Project Showcase**: Display projects in a responsive grid layout
- **Rich Media Support**: Add images, videos, and publications to each project
- **Tag-Based Filtering**: Organize and filter projects by tags
- **Search Functionality**: Search projects by title, description, or tags
- **Admin Interface**: Easy-to-use Django admin for managing projects
- **Responsive Design**: Mobile-friendly layout
- **Ordered by Date**: Projects automatically sorted by date, newest first

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or navigate to the project directory**:
   ```bash
   cd visionomy-django
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations** (already done, but if needed):
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser** for admin access:
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to set up your admin username, email, and password.

5. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the application**:
   - Website: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Usage

### Adding Projects

1. Log in to the admin panel at http://127.0.0.1:8000/admin/
2. Click on "Projects" under the Portfolio section
3. Click "Add Project" button
4. Fill in the project details:
   - **Title**: Project name
   - **Slug**: URL-friendly version (auto-generated from title)
   - **Short Description**: Brief description for the project tile
   - **Description**: Full project description
   - **Date**: Project completion or publication date
   - **Thumbnail**: Main image for the project tile
   - **Tags**: Select or create tags for categorization
   - **Featured**: Mark important projects as featured
   - **GitHub URL** and **Demo URL**: Optional links

5. Add related items using inline forms:
   - **Images**: Add multiple images with captions and ordering
   - **Videos**: Upload videos or provide YouTube/Vimeo URLs
   - **Publications**: Add research papers or articles

6. Click "Save" to publish the project

### Managing Tags

1. Go to the admin panel
2. Click on "Tags" under the Portfolio section
3. Add new tags with a name and slug
4. Tags can be assigned to multiple projects

## Project Structure

```
visionomy-django/
├── visionomy/              # Main project settings
│   ├── settings.py         # Django settings
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
├── portfolio/             # Portfolio app
│   ├── models.py          # Database models (Project, Tag, etc.)
│   ├── views.py           # View functions
│   ├── admin.py           # Admin interface configuration
│   ├── urls.py            # App URL patterns
│   └── templates/         # HTML templates
│       └── portfolio/
│           ├── base.html
│           ├── project_list.html
│           └── project_detail.html
├── static/                # Static files
│   └── css/
│       └── style.css      # Main stylesheet
├── media/                 # Uploaded files (created automatically)
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## Database Models

### Project
- Title, slug, description
- Short description for tiles
- Date, creation/update timestamps
- Thumbnail image
- Tags (many-to-many relationship)
- Featured flag
- GitHub and demo URLs

### Tag
- Name and slug for categorization

### ProjectImage
- Associated with a project
- Image file, caption, and display order

### ProjectVideo
- Associated with a project
- Video file or URL (YouTube, Vimeo)
- Caption and display order

### Publication
- Associated with a project
- Title, authors, venue, year
- URL and PDF file
- Abstract

## Customization

### Styling
Edit `static/css/style.css` to customize the appearance. The CSS uses CSS Grid for responsive layouts.

### Templates
Templates are located in `portfolio/templates/portfolio/`:
- `base.html`: Base template with navigation and footer
- `project_list.html`: Home page with project grid
- `project_detail.html`: Individual project page

### Settings
Edit `visionomy/settings.py` to configure:
- Database settings
- Static and media file locations
- Installed apps
- Security settings (for production)

## Production Deployment

Before deploying to production:

1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS` with your domain
3. Set up a proper database (PostgreSQL recommended)
4. Configure static file serving with a web server (Nginx, Apache)
5. Set up media file storage (local or cloud storage)
6. Use environment variables for sensitive settings
7. Enable HTTPS

## License

This project is provided as-is for portfolio purposes.
