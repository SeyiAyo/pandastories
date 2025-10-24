from django import template
from django.utils.safestring import mark_safe
import json
from datetime import datetime

register = template.Library()

@register.filter(is_safe=True)
def jsonld_blog_post(post):
    """Generate JSON-LD structured data for a blog post."""
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "description": post.meta_description or "",
        "author": {
            "@type": "Organization",
            "name": "My Panda Blog"
        },
        "datePublished": post.published_at.isoformat() if post.published_at else post.created_at.isoformat(),
        "dateModified": post.updated_at.isoformat(),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": post.get_absolute_url()
        },
        "keywords": [tag.name for tag in post.tags.all()],
        "articleSection": post.category.title,
    }
    
    if post.image:
        data["image"] = {
            "@type": "ImageObject",
            "url": post.image.url,
        }
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data)}</script>')

@register.simple_tag
def meta_tags(post=None, category=None):
    """Generate OpenGraph and Twitter meta tags."""
    tags = []
    
    if post:
        tags.extend([
            f'<meta property="og:title" content="{post.meta_title or post.title}">',
            f'<meta property="og:description" content="{post.meta_description}">',
            '<meta property="og:type" content="article">',
            f'<meta name="twitter:title" content="{post.meta_title or post.title}">',
            f'<meta name="twitter:description" content="{post.meta_description}">',
        ])
        
        if post.image:
            tags.extend([
                f'<meta property="og:image" content="{post.image.url}">',
                f'<meta name="twitter:image" content="{post.image.url}">',
            ])
    
    elif category:
        tags.extend([
            f'<meta property="og:title" content="{category.title}">',
            f'<meta property="og:description" content="{category.meta_description}">',
            '<meta property="og:type" content="website">',
        ])
    
    return mark_safe('\n'.join(tags))
