from textblob import TextBlob
from django.db.models import Count, Q
from django.utils.html import strip_tags

def get_sentiment(text):
    """Calculate sentiment score for given text."""
    if not text:
        return 0.0
    
    text = strip_tags(text)
    blob = TextBlob(text)
    return blob.sentiment.polarity

def recommend_posts(post, limit=3):
    """Recommend posts based on tags and category."""
    from .models import Post  # Import here to avoid circular import
    
    # Get posts with similar tags
    similar_posts = Post.objects.filter(status=Post.ACTIVE).exclude(id=post.id)
    
    # First try to find posts with matching tags
    if post.tags.exists():
        tag_ids = post.tags.values_list('id', flat=True)
        similar_posts = similar_posts.filter(tags__in=tag_ids).distinct()
        
        # Order by number of matching tags and creation date
        similar_posts = similar_posts.annotate(
            same_tags=Count('tags', filter=Q(tags__in=tag_ids))
        ).order_by('-same_tags', '-created_at')
        
        if similar_posts.exists():
            return similar_posts[:limit]
    
    # If no posts with matching tags, try posts from same category
    category_posts = similar_posts.filter(category=post.category).order_by('-created_at')
    if category_posts.exists():
        return category_posts[:limit]
    
    # If still no matches, return latest posts
    return similar_posts.order_by('-created_at')[:limit]

def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def track_post_view(request, post):
    """Track post view with user/session info."""
    from .models import PostView  # Import here to avoid circular import
    
    if not request.session.session_key:
        request.session.save()
    
    # Create PostView if it doesn't exist for this session/user
    PostView.objects.get_or_create(
        post=post,
        session_key=request.session.session_key,
        user=request.user if request.user.is_authenticated else None,
        ip_address=get_client_ip(request)
    )
