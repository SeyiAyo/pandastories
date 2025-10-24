from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-and-conditions/', views.terms_conditions, name='terms_conditions'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:post_slug>/', views.post_detail, name='post_detail'),
]
