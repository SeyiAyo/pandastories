"""
URL configuration for PandaStories project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from blog.sitemaps import PostSitemap, CategorySitemap
from django.contrib.sitemaps.views import sitemap
from blog import views

sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap
}

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Blog URLs
    path('', include('blog.urls')),
    
    # CKEditor 5
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    
    # Robots and sitemap
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Serve static and media files (works on Vercel)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)