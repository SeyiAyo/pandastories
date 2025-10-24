from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.utils import timezone
from .models import Post, Category, Comment, Newsletter, PostView, SavedPost
from taggit.models import Tag
from taggit.admin import TagAdmin as BaseTagAdmin

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'post_count', 'description_preview')
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('post_count',)
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Number of Posts'
    
    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Description'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'created_at', 'view_count', 'reading_time_display', 'featured', 'image_preview', 'tag_list')
    list_filter = ('status', 'category', 'created_at', 'featured')
    search_fields = ('title', 'content', 'meta_title', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 20
    list_editable = ('status', 'featured')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'status', 'featured')
        }),
        ('Content', {
            'fields': ('intro', 'content', 'image', 'video_url', 'tags')
        }),
        ('SEO & Meta', {
            'fields': ('meta_title', 'meta_description', 'canonical_url'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at', 'views_count')
    actions = ['make_published', 'make_draft', 'reset_views_count']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
    
    def tag_list(self, obj):
        return ", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'
    
    def view_count(self, obj):
        count = obj.post_views.count()
        url = reverse('admin:blog_postview_changelist') + f'?post__id__exact={obj.id}'
        return format_html('<a href="{}">{} views</a>', url, count)
    view_count.short_description = 'Views'
    
    def reading_time_display(self, obj):
        return f"{obj.reading_time} min read"
    reading_time_display.short_description = 'Reading Time'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; border-radius: 5px;"/>', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'
    
    def make_published(self, request, queryset):
        queryset.update(status=Post.ACTIVE, published_at=timezone.now())
    make_published.short_description = "Mark selected posts as published"
    
    def make_draft(self, request, queryset):
        queryset.update(status=Post.DRAFT, published_at=None)
    make_draft.short_description = "Mark selected posts as draft"
    
    def reset_views_count(self, request, queryset):
        queryset.update(views_count=0)
        PostView.objects.filter(post__in=queryset).delete()
    reset_views_count.short_description = "Reset view count"
    
    class Media:
        css = {
            'all': ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css']
        }

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'name', 'email', 'created_at', 'is_approved', 'content_preview')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'email', 'contents', 'post__title')
    date_hierarchy = 'created_at'
    list_per_page = 50
    list_editable = ('is_approved',)
    
    actions = ['approve_comments', 'unapprove_comments']
    
    def content_preview(self, obj):
        return obj.contents[:100] + '...' if len(obj.contents) > 100 else obj.contents
    content_preview.short_description = 'Comment Preview'
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = "Approve selected comments"
    
    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_comments.short_description = "Unapprove selected comments"

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at', 'last_sent')
    list_filter = ('is_active', 'created_at', 'last_sent')
    search_fields = ('email',)
    actions = ['send_newsletter']

    def send_newsletter(self, request, queryset):
        # For future newsletter sending functionality
        self.message_user(request, "Newsletter sending will be implemented in the next update.")
    send_newsletter.short_description = "Send newsletter to selected subscribers"

@admin.register(PostView)
class PostViewAdmin(admin.ModelAdmin):
    list_display = ('post', 'ip_address', 'session_key', 'created_at')
    list_filter = ('created_at', 'post')
    search_fields = ('post__title', 'ip_address', 'session_key')
    date_hierarchy = 'created_at'
    list_per_page = 100
    readonly_fields = ('post', 'ip_address', 'session_key', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display = ('post', 'ip_address', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('post__title', 'ip_address')

# Customize the existing TagAdmin
class CustomTagAdmin(BaseTagAdmin):
    list_display = ['name', 'slug', 'post_count']
    search_fields = ('name', 'slug')
    
    def post_count(self, obj):
        return obj.taggit_taggeditem_items.count()
    post_count.short_description = 'Number of Posts'

# Unregister the default TagAdmin and register our custom one
admin.site.unregister(Tag)
admin.site.register(Tag, CustomTagAdmin)

# Customize admin site header and title
admin.site.site_header = 'PandaStories Administration'
admin.site.site_title = 'PandaStories Admin'
admin.site.index_title = 'Dashboard'