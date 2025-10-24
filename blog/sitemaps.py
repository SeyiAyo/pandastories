from django.contrib.sitemaps import Sitemap
from .models import Post, Category
from django.shortcuts import reverse


class CategorySitemap(Sitemap):
    def items(self):
        return Category.objects.all()
    
    
class PostSitemap(Sitemap):
    def items(self):
        return Post.objects.filter(status=Post.ACTIVE)

    def lastmod(self, obj):
        return obj.created_at