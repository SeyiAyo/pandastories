from django.forms import ModelForm
from .models import Comment, Post, Newsletter
from django import forms


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'contents']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Your name',
                'required': True,
                'id': 'id_name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Your email',
                'required': True,
                'id': 'id_email'
            }),
            'contents': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Your comment',
                'rows': 4,
                'required': True,
                'id': 'id_contents'
            })
        }
        labels = {
            'name': 'Name',
            'email': 'Email',
            'contents': 'Comment'
        }
        error_messages = {
            'name': {
                'required': 'Please enter your name.',
            },
            'email': {
                'required': 'Please enter your email address.',
                'invalid': 'Please enter a valid email address.',
            },
            'contents': {
                'required': 'Please enter your comment.',
            },
        }
        
        
class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'intro', 'content', 'category', 'status', 'image', 'slug']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }),
            'intro': forms.Textarea(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500',
                'rows': 3
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500'
            })
        }


class NewsletterForm(forms.ModelForm):
    """Form for newsletter signup."""
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class': 'flex-1 rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500',
                'placeholder': 'Enter your email'
            }
        )
    )

    class Meta:
        model = Newsletter
        fields = ['email']