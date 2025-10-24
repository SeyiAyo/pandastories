from django.db import models
from django.utils.text import slugify
from django.utils.html import strip_tags
from django_ckeditor_5.fields import CKEditor5Field
from taggit.managers import TaggableManager

class Category(models.Model):
    """Category model for organizing blog posts."""
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(db_index=True, unique=True)
    description = models.TextField(blank=True)
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    
    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/category/{self.slug}/"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Post(models.Model):
    """Blog post model with modern features."""
    ACTIVE = 'active'
    DRAFT = 'draft'
    SCHEDULED = 'scheduled'
    
    CHOICES_STATUS = (
        (ACTIVE, 'Active'),
        (DRAFT, 'Draft'),
        (SCHEDULED, 'Scheduled'),
    )
    
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(db_index=True, unique=True)
    category = models.ForeignKey(Category, related_name="posts", on_delete=models.CASCADE)
    
    intro = CKEditor5Field(blank=True, null=True, config_name='default')
    content = CKEditor5Field(blank=True, null=True, config_name='default')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=CHOICES_STATUS, default=DRAFT)
    
    # Media
    image = models.ImageField(upload_to="uploads/", null=True, blank=True)
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    
    # SEO and metadata
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO meta title")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO meta description")
    canonical_url = models.URLField(blank=True, help_text="Canonical URL if this is a repost")
    
    # Analytics and engagement
    views_count = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)
    
    # Tags using django-taggit
    tags = TaggableManager(blank=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['created_at', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['status', 'published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/{self.category.slug}/{self.slug}/"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.meta_description:
            self.meta_description = strip_tags(self.intro)[:160] if self.intro else ""
        super().save(*args, **kwargs)
    
    @property
    def reading_time(self):
        """Calculate reading time in minutes based on content length."""
        text = strip_tags(self.content)
        words = len(text.split())
        minutes = round(words / 200)  # Average reading speed of 200 words per minute
        return max(1, minutes)  # Minimum 1 minute reading time

class Comment(models.Model):
    """Comment model for blog posts."""
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    contents = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"

class Newsletter(models.Model):
    """Newsletter subscription model."""
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-created_at']

class SavedPost(models.Model):
    """Model for saved posts."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['post', 'ip_address']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.post.title} saved by {self.ip_address}"

class PostView(models.Model):
    """Track post views."""
    post = models.ForeignKey(Post, related_name='post_views', on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]
    
    def __str__(self):
        return f"View of {self.post.title} at {self.created_at}"