from django.core.management.base import BaseCommand
from django.utils.text import slugify
from blog.models import Category, Post
from django.contrib.auth.models import User
from django.utils import timezone

class Command(BaseCommand):
    help = 'Adds sample blog posts and categories'

    def handle(self, *args, **kwargs):
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create categories
        categories_data = [
            {
                'title': 'Technology',
                'description': 'Latest technology trends and innovations'
            },
            {
                'title': 'Programming',
                'description': 'Programming tutorials and best practices'
            },
            {
                'title': 'Web Development',
                'description': 'Web development tips and techniques'
            },
            {
                'title': 'AI & Machine Learning',
                'description': 'Artificial Intelligence and Machine Learning insights'
            },
            {
                'title': 'Data Science',
                'description': 'Data analysis and visualization'
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                title=cat_data['title'],
                defaults={
                    'description': cat_data['description'],
                    'slug': slugify(cat_data['title'])
                }
            )
            categories[cat_data['title']] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category "{cat_data["title"]}"'))

        # Create posts
        posts_data = [
            {
                'category': 'Technology',
                'title': 'The Future of Quantum Computing',
                'intro': 'Exploring the revolutionary potential of quantum computers and their impact on technology',
                'body': '''
                <h2>Introduction to Quantum Computing</h2>
                <p>Quantum computing represents a paradigm shift in computational capabilities. Unlike classical computers that use bits, quantum computers use quantum bits or qubits.</p>
                
                <h2>Key Advantages</h2>
                <ul>
                    <li>Exponentially faster processing for certain problems</li>
                    <li>Better optimization capabilities</li>
                    <li>Enhanced cryptography potential</li>
                </ul>
                
                <h2>Current Challenges</h2>
                <p>Despite the promising future, quantum computing faces several challenges including:</p>
                <ul>
                    <li>Maintaining quantum coherence</li>
                    <li>Error correction</li>
                    <li>Scaling up qubit systems</li>
                </ul>
                ''',
                'featured': True
            },
            {
                'category': 'Programming',
                'title': 'Python vs JavaScript: A Developer\'s Guide',
                'intro': 'A comprehensive comparison of two of the most popular programming languages',
                'body': '''
                <h2>Language Characteristics</h2>
                <p>Python and JavaScript serve different primary purposes but have some overlapping use cases.</p>
                
                <h3>Python Strengths</h3>
                <ul>
                    <li>Data analysis and scientific computing</li>
                    <li>Backend web development</li>
                    <li>Artificial Intelligence and Machine Learning</li>
                </ul>
                
                <h3>JavaScript Strengths</h3>
                <ul>
                    <li>Frontend web development</li>
                    <li>Full-stack development with Node.js</li>
                    <li>Real-time applications</li>
                </ul>
                ''',
                'featured': False
            },
            {
                'category': 'Web Development',
                'title': 'Modern Web Development with React and Django',
                'intro': 'Building scalable web applications using React frontend and Django backend',
                'body': '''
                <h2>Full Stack Development</h2>
                <p>Combining React and Django creates a powerful stack for modern web applications.</p>
                
                <h3>Django Backend</h3>
                <ul>
                    <li>Robust ORM</li>
                    <li>Admin interface</li>
                    <li>REST framework</li>
                </ul>
                
                <h3>React Frontend</h3>
                <ul>
                    <li>Component-based architecture</li>
                    <li>Virtual DOM</li>
                    <li>Rich ecosystem</li>
                </ul>
                ''',
                'featured': True
            }
        ]

        for post_data in posts_data:
            post, created = Post.objects.get_or_create(
                title=post_data['title'],
                defaults={
                    'category': categories[post_data['category']],
                    'intro': post_data['intro'],
                    'content': post_data['body'],
                    'slug': slugify(post_data['title']),
                    'status': Post.ACTIVE,
                    'featured': post_data['featured'],
                    'created_at': timezone.now(),
                    'updated_at': timezone.now(),
                    'published_at': timezone.now()
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created post "{post_data["title"]}"'))
