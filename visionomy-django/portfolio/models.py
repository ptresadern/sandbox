from django.db import models
from django.utils import timezone


class Tag(models.Model):
    """Tag for categorizing projects"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Project(models.Model):
    """Portfolio project model"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, help_text="Brief description for project tiles")
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='projects', blank=True)
    featured = models.BooleanField(default=False, help_text="Display prominently on home page")
    thumbnail = models.ImageField(upload_to='projects/thumbnails/', null=True, blank=True)
    github_url = models.URLField(blank=True, null=True)
    demo_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date', '-created_at']


class ProjectImage(models.Model):
    """Images associated with a project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.project.title} - Image {self.order}"

    class Meta:
        ordering = ['order', 'id']


class ProjectVideo(models.Model):
    """Videos associated with a project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='projects/videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube, Vimeo, or other video URL")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.project.title} - Video {self.order}"

    class Meta:
        ordering = ['order', 'id']


class Publication(models.Model):
    """Publications/papers associated with a project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='publications')
    title = models.CharField(max_length=300)
    authors = models.CharField(max_length=500)
    venue = models.CharField(max_length=200, help_text="Conference, journal, or publication venue")
    year = models.PositiveIntegerField()
    url = models.URLField(blank=True, null=True)
    pdf = models.FileField(upload_to='projects/publications/', blank=True, null=True)
    abstract = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.year})"

    class Meta:
        ordering = ['-year', 'title']
