from django.contrib import admin
from .models import Tag, Project, ProjectImage, ProjectVideo, Publication


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'order']


class ProjectVideoInline(admin.TabularInline):
    model = ProjectVideo
    extra = 1
    fields = ['video', 'video_url', 'caption', 'order']


class PublicationInline(admin.TabularInline):
    model = Publication
    extra = 1
    fields = ['title', 'authors', 'venue', 'year', 'url', 'pdf']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'featured', 'created_at']
    list_filter = ['featured', 'date', 'tags']
    search_fields = ['title', 'description', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    date_hierarchy = 'date'
    inlines = [ProjectImageInline, ProjectVideoInline, PublicationInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description')
        }),
        ('Media', {
            'fields': ('thumbnail',)
        }),
        ('Metadata', {
            'fields': ('date', 'tags', 'featured')
        }),
        ('Links', {
            'fields': ('github_url', 'demo_url'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'caption', 'order']
    list_filter = ['project']
    search_fields = ['project__title', 'caption']


@admin.register(ProjectVideo)
class ProjectVideoAdmin(admin.ModelAdmin):
    list_display = ['project', 'caption', 'order']
    list_filter = ['project']
    search_fields = ['project__title', 'caption']


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ['title', 'authors', 'venue', 'year', 'project']
    list_filter = ['year', 'venue', 'project']
    search_fields = ['title', 'authors', 'venue', 'abstract']
