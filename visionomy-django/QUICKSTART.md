# Quick Start Guide

Get your portfolio website up and running in minutes!

## Quick Setup

```bash
# 1. Navigate to the project directory
cd visionomy-django

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Create an admin user
python manage.py createsuperuser

# 4. Start the development server
python manage.py runserver
```

## Access Your Site

- **Portfolio Website**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Adding Your First Project

1. Go to http://127.0.0.1:8000/admin/
2. Log in with your superuser credentials
3. Click **"+ Add"** next to **Projects**
4. Fill in the basic info:
   - **Title**: "My Awesome Project"
   - **Slug**: "my-awesome-project" (auto-fills)
   - **Short description**: "A brief one-liner about your project"
   - **Description**: Full details about what you built
   - **Date**: When you completed it
5. Optionally add:
   - A thumbnail image
   - Tags (create them first in the Tags section)
   - Images, videos, and publications using the inline forms
6. Click **"Save"**
7. Visit http://127.0.0.1:8000/ to see your project!

## Tips

### Creating Tags
Before adding projects, create some tags:
1. Admin Panel → Tags → Add Tag
2. Examples: "Python", "Django", "Machine Learning", "Web Development"
3. The slug auto-generates from the name

### Adding Images
- Use the **ProjectImage** inline form at the bottom of the project edit page
- Upload multiple images per project
- Use the **order** field to control display order
- Add captions to describe each image

### Adding Videos
- Upload video files directly, OR
- Paste YouTube/Vimeo URLs in the **video_url** field
- Both work seamlessly in the frontend

### Adding Publications
- Great for research projects or blog posts
- Add author names, venue, year
- Upload PDFs or link to online versions
- Include abstracts for context

## Searching & Filtering

Once you have projects:
- Use the search bar on the homepage
- Click tags to filter projects
- All filters work together

## Next Steps

- Customize the CSS in `static/css/style.css`
- Add your branding to templates
- Create more projects!
- Deploy to production when ready

## Need Help?

Check the full README.md for detailed documentation.
