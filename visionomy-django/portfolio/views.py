from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Project, Tag


def project_list(request):
    """Display all projects in a grid, ordered by date (newest first)"""
    projects = Project.objects.all().prefetch_related('tags', 'images')

    # Get all tags for the filter sidebar
    all_tags = Tag.objects.all()

    # Filter by tag if provided
    tag_slug = request.GET.get('tag')
    if tag_slug:
        projects = projects.filter(tags__slug=tag_slug)
        selected_tag = get_object_or_404(Tag, slug=tag_slug)
    else:
        selected_tag = None

    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()

    context = {
        'projects': projects,
        'all_tags': all_tags,
        'selected_tag': selected_tag,
        'search_query': search_query,
    }

    return render(request, 'portfolio/project_list.html', context)


def project_detail(request, slug):
    """Display detailed view of a single project"""
    project = get_object_or_404(
        Project.objects.prefetch_related('images', 'videos', 'publications', 'tags'),
        slug=slug
    )

    context = {
        'project': project,
    }

    return render(request, 'portfolio/project_detail.html', context)
