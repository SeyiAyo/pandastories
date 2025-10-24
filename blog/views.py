from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.db.models import Prefetch
from django.contrib import messages

from .models import Post, Category, Comment, Newsletter, PostView, SavedPost
from .forms import CommentForm, NewsletterForm
from .utils import get_sentiment, recommend_posts
from django.db.models import Count

def frontpage(request):
    """View for the front page of the blog."""
    # Get cached categories or fetch and cache them
    categories = cache.get('all_categories')
    if categories is None:
        categories = Category.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status=Post.ACTIVE))
        ).order_by('title')
        cache.set('all_categories', categories, 60 * 60)  # Cache for 1 hour
    
    featured_posts = Post.objects.filter(
        status=Post.ACTIVE, 
        featured=True
    ).select_related(
        'category'
    ).prefetch_related(
        'tags'
    ).annotate(
        comment_count=Count('comments', filter=Q(comments__is_approved=True))
    ).order_by('-created_at')[:3]
    
    posts = Post.objects.filter(
        status=Post.ACTIVE
    ).select_related(
        'category'
    ).prefetch_related(
        'tags'
    ).annotate(
        comment_count=Count('comments', filter=Q(comments__is_approved=True))
    ).order_by('-created_at')

    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
    }
    
    return render(request, 'frontpage.html', context)

@cache_page(60 * 60 * 24)  # Cache for 24 hours
def about(request):
    """Display the about page."""
    return render(request, 'about.html')

def contact(request):
    """Display the contact page."""
    context = {}
    return render(request, 'contact.html', context)

def post_detail(request, category_slug, post_slug):
    """Display a single post with its comments and recommendations."""
    # Try to get post from cache
    cache_key = f'post_{category_slug}_{post_slug}'
    post = cache.get(cache_key)
    
    if post is None:
        post = get_object_or_404(
            Post.objects.select_related('category').prefetch_related(
                Prefetch(
                    'comments',
                    queryset=Comment.objects.filter(is_approved=True).order_by('-created_at'),
                    to_attr='approved_comments'
                ),
                'tags'
            ).annotate(
                comment_count=Count('comments', filter=Q(comments__is_approved=True))
            ),
            category__slug=category_slug,
            slug=post_slug,
            status=Post.ACTIVE
        )
        cache.set(cache_key, post, 60 * 15)  # Cache for 15 minutes
    
    # Track post view
    if not request.session.session_key:
        request.session.save()
    
    # Get IP address
    ip_address = request.META.get('REMOTE_ADDR')
    
    # Create or get PostView
    PostView.objects.get_or_create(
        post=post,
        session_key=request.session.session_key,
        ip_address=ip_address
    )
    
    # Check if post is saved by current IP
    is_saved = SavedPost.objects.filter(post=post, ip_address=ip_address).exists()
    
    # Get related posts based on tags
    post_tags_ids = post.tags.values_list('id', flat=True)
    related_posts = Post.objects.filter(
        status=Post.ACTIVE,
        tags__in=post_tags_ids
    ).exclude(
        id=post.id
    ).select_related(
        'category'
    ).prefetch_related(
        'tags'
    ).annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags', '-created_at')[:3]
    
    # Handle form submissions
    if request.method == 'POST':
        if 'save_post' in request.POST:
            if is_saved:
                SavedPost.objects.filter(post=post, ip_address=ip_address).delete()
                messages.success(request, 'Post removed from saved items.')
            else:
                SavedPost.objects.create(post=post, ip_address=ip_address)
                messages.success(request, 'Post saved successfully.')
            return redirect('post_detail', category_slug=category_slug, post_slug=post_slug)
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, 'Your comment has been submitted for approval.')
            return redirect('post_detail', category_slug=category_slug, post_slug=post_slug)
    else:
        form = CommentForm()
    
    context = {
        'post': post,
        'form': form,
        'is_saved': is_saved,
        'related_posts': related_posts,
    }
    
    return render(request, 'post_detail.html', context)

def category_detail(request, slug):
    """Display posts for a specific category."""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category, 
        status=Post.ACTIVE
    ).select_related(
        'category'
    ).annotate(
        comment_count=Count('comments', filter=Q(comments__is_approved=True))
    ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'posts': posts,
    }
    
    return render(request, 'category_detail.html', context)

def search(request):
    """Search posts by query string."""
    query = request.GET.get('query', '')
    posts = Post.objects.filter(status=Post.ACTIVE).select_related('category')
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(intro__icontains=query) |
            Q(content__icontains=query)
        )
    
    # Get all categories for sidebar
    categories = Category.objects.all().annotate(
        post_count=Count('posts', filter=Q(posts__status=Post.ACTIVE))
    )
    
    return render(request, 'search.html', {
        'query': query, 
        'posts': posts, 
        'categories': categories
    })

def newsletter_signup(request):
    """Handle newsletter signups."""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not Newsletter.objects.filter(email=email).exists():
                newsletter = Newsletter.objects.create(
                    email=email,
                    is_active=True
                )
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            else:
                messages.info(request, 'You are already subscribed to our newsletter.')
        else:
            messages.error(request, 'Please enter a valid email address.')
    
    return redirect(request.META.get('HTTP_REFERER', 'blog:frontpage'))

def privacy_policy(request):
    """Display the privacy policy page."""
    return render(request, 'privacy_policy.html')

def terms_conditions(request):
    """Display the terms and conditions page."""
    return render(request, 'terms_conditions.html')

def robots_txt(request):
    """Serve robots.txt file."""
    content = """
    User-agent: *
    Disallow: /admin/
    Disallow: /search/
    Allow: /
    """
    return HttpResponse(content, content_type='text/plain')